# 抓取 COM10 串口日志。用法：powershell & "E:\QRS\Project\xiaozhi\xiaozhi_xiage\capture_serial.ps1" [秒数]
param([int]$Seconds = 45)
$PythonExe = 'C:\Users\a\.platformio\penv\Scripts\python.exe'
$OUT = "E:\QRS\Project\xiaozhi\xiaozhi_xiage\serial_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$ScriptPath = "$env:TEMP\wb_cap.py"

$code = @'
import serial, sys, time
port = sys.argv[1]; out = sys.argv[2]; dur = float(sys.argv[3])
s = serial.Serial(port, 115200, timeout=0.5)
f = open(out, "wb", buffering=0)
t0 = time.time()
print("CAPTURE_START", flush=True)
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