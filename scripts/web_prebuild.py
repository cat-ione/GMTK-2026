#!/usr/bin/env python3
"""
web-prebuild: apply CPython -O / -OO source transformations to a project
before packaging with pygbag, since pygbag ships .py source that the in-browser
runtime compiles at optimize level 0 (so asserts and __debug__ blocks survive).

Usage:
    python web_prebuild.py <src_dir> <out_dir> [--oo]

Then:  pygbag --build <out_dir>/main.py
"""
import ast, sys, os, shutil
from pathlib import Path

# Directories never worth packaging for a pygbag build (mirrors pygbag's own
# ignore intent). The output dir is added dynamically so we never re-consume it.
IGNORE_DIRS = {
    ".git", ".github", ".hg", ".svn", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".venv", "venv", "env", "node_modules",
    "build", "dist", ".idea", ".vscode",
    # Custom dirs and files
    "dumps", "scripts"
}


class OptimizeTransformer(ast.NodeTransformer):
    def __init__(self, strip_docstrings=False):
        self.strip_docstrings = strip_docstrings

    # -O: drop assert statements
    def visit_Assert(self, node):
        return None

    # -O: __debug__ is the constant False under optimization
    def visit_Name(self, node):
        if node.id == "__debug__" and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.Constant(value=False), node)
        return node

    # -O: prune `if __debug__:` -> keep only the else branch (dead-branch elim)
    def visit_If(self, node):
        self.generic_visit(node)
        test = node.test
        if isinstance(test, ast.Constant):
            body = node.body if test.value else node.orelse
            if not body:
                return ast.copy_location(ast.Pass(), node)  # keep block valid
            return body  # splice surviving branch into parent
        return node

    # -OO: strip docstrings
    def _strip_doc(self, node):
        if not self.strip_docstrings:
            return
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            node.body.pop(0)
            if not node.body:
                node.body.append(ast.copy_location(ast.Pass(), node))

    def visit_FunctionDef(self, node):
        self.generic_visit(node); self._strip_doc(node); return node
    visit_AsyncFunctionDef = visit_FunctionDef # type: ignore
    def visit_ClassDef(self, node):
        self.generic_visit(node); self._strip_doc(node); return node
    def visit_Module(self, node):
        self.generic_visit(node); self._strip_doc(node); return node


# Suites that are ILLEGAL when empty (must get a `pass`). orelse / finalbody /
# handler-lists are legal when empty (they just mean "clause absent"), so a
# removed assert there needs no filler.
_REQUIRED_BODIES = (
    ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
    ast.If, ast.For, ast.AsyncFor, ast.While,
    ast.With, ast.AsyncWith, ast.Try, ast.ExceptHandler,
)
if hasattr(ast, "match_case"):
    _REQUIRED_BODIES += (ast.match_case,)


def _repair_empty(tree):
    for node in ast.walk(tree):
        if isinstance(node, _REQUIRED_BODIES) and not node.body:
            node.body.append(ast.copy_location(ast.Pass(), node))
        # try/except: each handler body is also required
        if isinstance(node, ast.Try):
            for h in node.handlers:
                if not h.body:
                    h.body.append(ast.copy_location(ast.Pass(), h))
    return tree


def transform_source(src: str, strip_docstrings=False) -> str:
    tree = ast.parse(src)
    tree = OptimizeTransformer(strip_docstrings).visit(tree)
    _repair_empty(tree)
    ast.fix_missing_locations(tree)
    # sanity: the result must recompile
    compile(tree, "<transformed>", "exec")
    return ast.unparse(tree)


def main():
    argv = sys.argv[1:]
    oo = any(a in ("-OO", "--oo") for a in argv)          # -OO / --oo => strip docstrings
    positional = [a for a in argv if not a.startswith("-")]  # -O / -OO consumed here
    if len(positional) < 2:
        sys.exit("usage: pygbag_prebuild.py <src_dir> <out_dir> [-O|-OO]")
    src_dir = Path(positional[0]).resolve()
    out_dir = Path(positional[1]).resolve()

    if out_dir == src_dir:
        sys.exit("error: out_dir must differ from src_dir")
    if out_dir.exists():
        shutil.rmtree(out_dir)

    n_opt = n_copy = n_skip = 0
    for root, dirs, files in os.walk(src_dir):
        rootp = Path(root)
        # prune: junk dirs, hidden dirs, and the output dir itself
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
            and not d.startswith(".")
            and (rootp / d).resolve() != out_dir
        ]
        for fn in files:
            if fn.startswith("."):
                continue
            srcf = rootp / fn
            rel = srcf.relative_to(src_dir)
            dstf = out_dir / rel
            dstf.parent.mkdir(parents=True, exist_ok=True)
            if srcf.suffix == ".py" and not (fn == "main.py" and rootp == src_dir):
                try:
                    dstf.write_text(
                        transform_source(srcf.read_text(encoding="utf-8"),
                                          strip_docstrings=oo),
                        encoding="utf-8",
                    )
                    print(f"opt  {rel}")
                    n_opt += 1
                except (SyntaxError, ValueError) as e:
                    shutil.copy2(srcf, dstf)  # unparseable: pass through untouched
                    print(f"skip {rel}  ({type(e).__name__}, copied verbatim)")
                    n_skip += 1
            else:
                shutil.copy2(srcf, dstf)
                n_copy += 1

    mode = "-OO" if oo else "-O"
    print(f"\n{mode}: {n_opt} optimized, {n_copy} copied, {n_skip} skipped")
    print(f"next: pygbag --build {out_dir / 'main.py'}")


if __name__ == "__main__":
    main()
