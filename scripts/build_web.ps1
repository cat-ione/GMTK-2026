param(
    [switch]$r
)

uv run scripts\web_prebuild.py . build\web -OO
pygbag --PYBUILD 3.14 --can_close 1 --disable-sound-format-error --archive build\web\main.py
cp build\web\build\web.zip dist

if ($r) {
    pygbag --PYBUILD 3.14 --can_close 1 --disable-sound-format-error build\web\main.py
}
