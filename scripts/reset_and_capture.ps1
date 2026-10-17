# 复位 COM10 上的 ESP32-C6 并抓日志
# 用法: & "<repo>\reset_and_capture.ps1" [秒数]
param([int]$Seconds = 120)
$PythonExe = '<home>\.platformio\penv\Scripts\python.exe'
$OUT = "<repo>\serial_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$ScriptPath = "$env:TEMP\wb_reset_cap.py"

$code = @'
import serial, sys, time
port = sys.argv[1]; out = sys.argv[2]; dur = float(sys.argv[3])
s = serial.Serial(port, 115200, timeout=0.2)
# CH343: DTR->EN(低有效), RTS->BOOT(低有效进下载)
# 保持 RTS 高电平(不进下载), 用 DTR 低脉冲复位
s.dtr = False
s.rts = True
time.sleep(0.1)
s.dtr = True      # EN 拉低 -> 复位
time.sleep(0.15)
s.dtr = False     # EN 释放
time.sleep(0.3)
print("RESET_PULSED", flush=True)
t0 = time.time()
f = open(out, "wb", buffering=0)
while time.time() - t0 < dur:
    b = s.read(4096)
    if b:
        f.write(b)
        sys.stdout.write(b.decode("utf-8", "ignore"))
        sys.stdout.flush()
f.close()
print("\nCAPTURE_DONE", out, flush=True)
'@

$code | Out-File -FilePath $ScriptPath -Encoding ascii
& $PythonExe $ScriptPath "COM10" $OUT $Seconds
Write-Output "LOG=$OUT"