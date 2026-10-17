import serial, time, re, sys

port = 'COM10'
rounds = 3
PAT = re.compile(rb'waiting 600ms[^\r\n]*|probe \w+: addr=0x[0-9A-Fa-f]+ @ \d+Hz \(\d+/\d+\)|OLED detected[^\r\n]*|No OLED found[^\r\n]*|Install SSD1306 driver|SSD1306 driver installed|Turning display on|OLED IS LIVE|late HIT[^\r\n]*|OLED WATCH[^\r\n]*|Failed to initialize[^\r\n]*|failed: \w+|abort\(\)[^\r\n]*')

s = serial.Serial(port, 115200, timeout=0.3)

for r in range(1, rounds + 1):
    s.reset_input_buffer()
    # 复位脉冲
    s.dtr = False
    s.rts = True
    time.sleep(0.1)
    s.dtr = True
    time.sleep(0.15)
    s.dtr = False
    # CH343 需要时间重新枚举，太早读会只拿到开头一截
    time.sleep(2.5)
    s.reset_input_buffer()

    t0 = time.time()
    buf = []
    while time.time() - t0 < 6.0:
        b = s.read(4096)
        if b:
            buf.append(b)
    raw = b''.join(buf)
    with open(r'<repo>\boot_%d.log' % r, 'wb') as f:
        f.write(raw)
    hits = PAT.findall(raw)
    print('=== BOOT ROUND %d  bytes=%d  hits=%d ===' % (r, len(raw), len(hits)))
    for h in hits:
        print('   ', h.decode('utf-8', 'ignore').strip())
    print(flush=True)
    time.sleep(2)

s.close()
print('ALLDONE')