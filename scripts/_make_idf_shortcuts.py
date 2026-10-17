"""Rebuild the ESP-IDF desktop shortcuts.

Why this exists: COM instantiation (WScript.Shell / IShellLink) is blocked on
this machine, and hand-patching the existing .lnk files was not possible
either, so the MS-SHLLINK bytes are emitted directly.

Header layout was verified against a Windows-authored file
(C:\\Users\\a\\Desktop\\tools\\ESP-IDF 5.5 CMD.lnk):
    0x00 HeaderSize 0x4C | 0x04 LinkCLSID | 0x14 LinkFlags
    0x18 FileAttributes | 0x1C CreationTime | 0x24 AccessTime
    0x2C WriteTime | 0x34 FileSize | 0x38 IconIndex | 0x3C ShowCommand
    0x40 HotKey | 0x42 Reserved | 0x44 Reserved2 | 0x48 pad -> 0x4C

The .cmd launchers it points at are the real work; the .lnk files only give
them a proper icon and a double-clickable name.

Run:  python _make_idf_shortcuts.py
"""
import struct, os

LINK_CLSID = bytes.fromhex('0102140000000000c000000000000046')

HAS_LINK_INFO        = 0x00000002
HAS_NAME             = 0x00000004
HAS_WORKING_DIR      = 0x00000010
HAS_ICON_LOCATION    = 0x00000040
IS_UNICODE           = 0x00000080
DISABLE_KNOWN_FOLDER = 0x00001000

DESKTOP = r'C:\Users\a\Desktop'
EIM = r'E:\app1\ESP\eim\eim.exe'


def header(show_command):
    h = struct.pack('<I', 0x4C) + LINK_CLSID
    h += struct.pack('<I', 0)          # LinkFlags, patched by caller
    h += struct.pack('<I', 0x20)       # FileAttributes = ARCHIVE
    h += b'\x00' * 24                  # Creation/Access/Write FILETIME
    h += struct.pack('<I', 0)          # FileSize
    h += struct.pack('<I', 0)          # IconIndex
    h += struct.pack('<I', show_command)
    h += struct.pack('<H', 0)          # HotKey
    h += struct.pack('<H', 0)          # Reserved
    h += struct.pack('<I', 0)          # Reserved2
    h += b'\x00' * 4                   # pad so the header is exactly 0x4C
    assert len(h) == 0x4C, len(h)
    return h


def link_info(target):
    """LocalBasePath (null-terminated UTF-16) + empty VolumeID, no UNC parts."""
    lbp = target.encode('utf-16-le') + b'\x00\x00'
    hdr_size = 0x1C
    local_base_off = hdr_size
    common_path_off = local_base_off + len(lbp)
    volume_id_off = common_path_off
    volume_id = struct.pack('<IIII', 0x10, 3, 0, 0x10)

    total = volume_id_off + len(volume_id)
    out = struct.pack('<IIIIIII', total, hdr_size, 0,
                      volume_id_off, local_base_off, 0, common_path_off)
    out += lbp + volume_id
    assert len(out) == total, (len(out), total)
    return out


def strings(name, working_dir, icon_loc):
    """StringData: NAME, RELATIVE_PATH, WORKING_DIR, ARGUMENTS, ICON_LOCATION."""
    out = b''
    for s in (name, '', working_dir, '', icon_loc):
        b = s.encode('utf-16-le')
        out += struct.pack('<H', len(s)) + b + b'\x00\x00'
    return out


def make_lnk(target, name, working_dir='', icon_loc='', show_command=7):
    flags = HAS_LINK_INFO | HAS_NAME | IS_UNICODE | DISABLE_KNOWN_FOLDER
    if working_dir:
        flags |= HAS_WORKING_DIR
    if icon_loc:
        flags |= HAS_ICON_LOCATION
    h = bytearray(header(show_command))
    h[0x14:0x18] = struct.pack('<I', flags)
    return bytes(h) + link_info(target) + strings(name, working_dir, icon_loc)


def parse(data):
    """Read the bytes back so a format mistake fails here, not in Explorer."""
    out = {}
    assert struct.unpack_from('<I', data, 0)[0] == 0x4C
    assert data[4:20] == LINK_CLSID
    out['flags'] = struct.unpack_from('<I', data, 0x14)[0]
    out['show_command'] = struct.unpack_from('<I', data, 0x3C)[0]

    off = 0x4C
    link_size = struct.unpack_from('<I', data, off)[0]
    hdr_size, _, vol_off, lbp_off, _, cps_off = struct.unpack_from('<IIIIII', data, off + 4)
    out['linkinfo_size'] = link_size
    assert hdr_size == 0x1C, hdr_size
    p = off + lbp_off
    end = p
    while data[end:end + 2] != b'\x00\x00':
        end += 2
    out['target'] = data[p:end].decode('utf-16-le')
    assert off + vol_off == end + 2, 'VolumeID must follow LocalBasePath'
    assert off + cps_off == end + 2, 'CommonPathSuffix offset mismatch'
    assert struct.unpack_from('<I', data, off + vol_off)[0] == 0x10
    off += link_size

    def take():
        nonlocal off
        count = struct.unpack_from('<H', data, off)[0]
        off += 2
        s = data[off:off + count * 2].decode('utf-16-le')
        off += count * 2 + 2
        return s

    out['name'] = take()
    take()                              # relative path (unused)
    out['working_dir'] = take()
    take()                              # arguments (unused)
    out['icon_location'] = take()
    out['consumed_all_bytes'] = (off == len(data))
    return out


JOBS = [
    ('IDF_v6.1_PowerShell.lnk', 'IDF_v6.1_PowerShell.cmd', DESKTOP,
     'ESP-IDF 6.1 PowerShell'),
    ('IDF_v6.1_CMD.lnk', 'IDF_v6.1_CMD.cmd', DESKTOP, 'ESP-IDF 6.1 CMD'),
    ('IDF_v6.1_小智工程.lnk', 'IDF_v6.1_小智工程.cmd', DESKTOP,
     'ESP-IDF 6.1 xiaozhi project'),
    ('ESP-IDF 安装管理器 (EIM).lnk', EIM, os.path.dirname(EIM),
     'ESP-IDF Installation Manager'),
]


def main():
    lines = []
    for lnk_name, target, wd, desc in JOBS:
        tpath = target if os.path.exists(target) else os.path.join(DESKTOP, target)
        assert os.path.exists(tpath), 'MISSING TARGET: ' + tpath
        show = 7 if tpath.lower().endswith('.cmd') else 1
        blob = make_lnk(tpath, desc, wd, EIM + ',0', show)
        p = parse(blob)
        assert p['target'] == tpath, (p['target'], tpath)
        assert p['consumed_all_bytes'], 'trailing bytes -> malformed'
        with open(os.path.join(DESKTOP, lnk_name), 'wb') as f:
            f.write(blob)
        lines.append('WROTE %s  (%d bytes)  ->  %s' % (lnk_name, len(blob), tpath))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '_lnk_write_log.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()