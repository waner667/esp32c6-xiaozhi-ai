import serial, sys, time, re

port = 'COM10'
dur = 25.0

s = serial.Serial(port, 115200, timeout=0.5)
t0 = time.time()
buf = []
while time.time() - t0 < dur:
    b = s.read(4096)
    if b:
        buf.append(b)
raw = b''.join(buf)
out = r'<repo>\listen.log'
with open(out, 'wb') as f:
    f.write(raw)

PAT = re.compile(rb'probe \w+: addr=0x[0-9A-Fa-f]+ @ \d+Hz \(\d+/\d+\)|weak: addr[^\r\n]*|OLED detected[^\r\n]*|No OLED found[^\r\n]*|Install SSD1306 driver|SSD1306 driver installed|Failed to initialize[^\r\n]*|failed: \w+|abort\(\)[^\r\n]*|free sram[^\r\n]*|Board: UUID[^\r\n]*')
print('bytes=%d' % len(raw))
for m in PAT.findall(raw):
    print('   ', m.decode('utf-8', 'ignore').strip())
print('DONE')