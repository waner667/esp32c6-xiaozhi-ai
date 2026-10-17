import io, os, sys

base = r'<repo>\me\xiaozhi-esp32-2.5.2\build'
OLD_BS = 'C:' + chr(92) + 'Espressif'
NEW_BS = 'E:' + chr(92) + 'app1' + chr(92) + 'ESP' + chr(92) + 'Espressif'
OLD_FW = 'C:/Espressif'
NEW_FW = '<app>\ESP/Espressif'

total = 0
files = 0
exts = ('.ninja', '.cmake', '.txt', '.json', '.rsp', '.cmake.in')
for root, dirs, names in os.walk(base):
    for n in names:
        if not n.endswith(exts):
            continue
        p = os.path.join(root, n)
        try:
            s = io.open(p, encoding='utf-8', errors='surrogateescape').read()
        except Exception:
            continue
        c = s.count(OLD_BS) + s.count(OLD_FW)
        if c:
            s2 = s.replace(OLD_BS, NEW_BS).replace(OLD_FW, NEW_FW)
            io.open(p, 'w', encoding='utf-8', errors='surrogateescape').write(s2)
            total += c
            files += 1
print('FILES=%d OCCURRENCES=%d' % (files, total))