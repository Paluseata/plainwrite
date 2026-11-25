# Reads LibreOffice's Hangul->Hanja character table (i18npool hhc_char, MPL 2.0) out of libtextconv_dict.so
import ctypes, sys, json
lib = ctypes.CDLL('/usr/lib/libreoffice/program/libtextconv_dict.so')
class HI(ctypes.Structure):
    _fields_ = [('code', ctypes.c_uint16), ('address', ctypes.c_uint16), ('count', ctypes.c_int16)]
lib.getHangul2HanjaData.restype = ctypes.POINTER(ctypes.c_uint16)
lib.getHangul2HanjaIndex.restype = ctypes.POINTER(HI)
lib.getHangul2HanjaIndexCount.restype = ctypes.c_int16
data = lib.getHangul2HanjaData(); idx = lib.getHangul2HanjaIndex(); n = lib.getHangul2HanjaIndexCount()
out = {}
for i in range(n):
    e = idx[i]
    raw = b''.join(data[e.address + j].to_bytes(2,'little') for j in range(e.count))
    out[chr(e.code)] = raw.decode('utf-16-le')
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False)
print(n, sum(len(v) for v in out.values()))
for k in ['한','국','학','생','대','가','사']: print(k, out.get(k, '')[:30])
