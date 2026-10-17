import serial, sys, time, re

port = 'COM10'
dur = 8.0
rounds = 4

s = serial.Serial(port, 115200, timeout=0.2)
PAT = re.compile(rb'probe |OLED detected|No OLED found|Install SSD1306|SSD1306 driver installed|failed|abort')


def reset():
    s.reset_input_buffer()
    s.dtr = False
    s.rts = True
    time.sleep(0.1)
    s.dtr = True      # EN拉低
    time.sleep(0.15)
    s.dtr = False     # EN释放
    time.sleep(0.3)


for r in range(1, rounds + 1):
    reset()
    t0 = time.time()
    buf = []
    while time.time() - t0 < dur:
        b = s.read(4096)
        if b:
            buf.append(b)
    raw = b''.join(buf)
    out = r'E:\QRS\Project\xiaozhi\xiaozhi_xiage\round_%d.log' % r
    with open(out, 'wb') as f:
        f.write(raw)
    hits = [m.decode('utf-8', 'ignore') for m in PAT.findall(raw)]
    print('ROUND %d  bytes=%d' % (r, len(raw)))
    for h in hits:
        print('   ', h.strip())
    if not hits:
        print('    (no probe lines captured)')
    print(flush=True)
    time.sleep(1)

s.close()
print('ALLDONE')