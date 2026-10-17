$ErrorActionPreference = 'Continue'
$TOOLS = '<app>\ESP\Espressif\tools'
$IDF   = '<IDF_PATH>'
$PYENV = '<app>\ESP\Espressif\python_env\idf6.1_py3.13_env'
$PROJ  = '<repo>\me\xiaozhi-esp32-2.5.2'
$BUILD = "$PROJ\build"

$env:IDF_PATH = $IDF
$env:IDF_TOOLS_PATH = $TOOLS
$env:IDF_PYTHON_ENV_PATH = $PYENV

$extra = @()
foreach ($p in @(
  "$TOOLS\ninja\1.12.1",
  "$TOOLS\cmake\3.30.2",
  "$TOOLS\ccache\4.12.1\ccache-4.12.1-windows-x86_64",
  "$TOOLS\riscv32-esp-elf\esp-15.2.0_20251204\riscv32-esp-elf\bin",
  "$IDF\tools"
)) { if (Test-Path $p) { $extra += $p } }
$env:PATH = ($extra -join ';') + ';' + $PYENV + '\Scripts;' + $env:PATH

# 把被占用导致编译失败的 display 相关 obj 清掉（改名为 .bak，避免删不掉）
$disp = Join-Path $BUILD 'esp-idf\main\CMakeFiles\__idf_main.dir\display'
if ($disp -and (Test-Path -LiteralPath $disp)) {
  Get-ChildItem $disp -Filter *.obj* -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $bak = $_.FullName + '.stale'
    try { Move-Item -LiteralPath $_.FullName -Destination $bak -Force -ErrorAction Stop }
    catch { Write-Output ("SKIP(rename fail): " + $_.Name) }
  }
}

Set-Location $BUILD
Write-Output "=== BUILD START ==="
& "$TOOLS\ninja\1.12.1\ninja.exe" -j 4
$rc = $LASTEXITCODE
Write-Output "=== BUILD_EXIT=$rc ==="
if (Test-Path "$BUILD\xiaozhi.bin") {
  Get-Item "$BUILD\xiaozhi.bin" | ForEach-Object {
    Write-Output ("BIN=" + $_.FullName + " SIZE=" + $_.Length + " MTIME=" + $_.LastWriteTime)
  }
}
exit $rc