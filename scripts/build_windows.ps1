param(
    [switch]$r
)

pyinstaller scripts\windows.spec --clean
if ($r -and $?) {
    echo "Build successful, running..."
    .\dist\windows.exe
}
