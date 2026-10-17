# 一键烧录 C6 固件 —— 用法：PowerShell 里执行 & "E:\QRS\Project\xiaozhi\xiaozhi_xiage\flash_c6.ps1"
# 前置：板子已上电、COM10 是 CH343、烧录包 flash_c6_tf1990\ 5 文件齐全
# 注意：COM10 不能被其他程序占用（串口助手/上位机要先关）

$PythonExe = 'C:\Users\a\.platformio\penv\Scripts\python.exe'
$LIB  = 'E:\QRS\Project\xiaozhi\xiaozhi_xiage\.esptool_lib'
$PKG  = 'E:\QRS\Project\xiaozhi\xiaozhi_xiage\flash_c6_tf1990'
$PORT = 'COM10'
$LOG  = 'E:\QRS\Project\xiaozhi\xiaozhi_xiage\flash_c6.log'

$env:PYTHONPATH = $LIB
Set-Location $PKG

Write-Output "=== FLASH START ($PORT) ==="
& $PythonExe -m esptool --chip esp32c6 --port $PORT --baud 460800 `
  write-flash --flash-mode dio --flash-size 16MB --flash-freq 80m `
  0x0    bootloader.bin `
  0x8000 partition-table.bin `
  0xd000 ota_data_initial.bin `
  0x20000 xiaozhi.bin `
  0x800000 generated_assets.bin 2>&1 |
  Tee-Object -FilePath $LOG

$rc = $LASTEXITCODE
Write-Output "=== FLASH_EXIT=$rc ==="
exit $rc