import sys
sys.stdout = open("log.txt","w")
sys.stderr = sys.stdout
import struct, ctypes, ctypes.util

cf = ctypes.CDLL(ctypes.util.find_library('CoreFoundation'))
imgio = ctypes.CDLL(ctypes.util.find_library('ImageIO'))
cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
cf.CFURLCreateFromFileSystemRepresentation.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_bool]
imgio.CGImageSourceCreateWithURL.restype = ctypes.c_void_p
imgio.CGImageSourceCreateWithURL.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
imgio.CGImageSourceCopyPropertiesAtIndex.restype = ctypes.c_void_p
imgio.CGImageSourceCopyPropertiesAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]
cf.CFDictionaryGetCount.restype = ctypes.c_long
cf.CFDictionaryGetCount.argtypes = [ctypes.c_void_p]
cf.CFRelease.restype = None
cf.CFRelease.argtypes = [ctypes.c_void_p]

print("START", flush=True)

base = bytearray([
    0xFF,0xD8,0xFF,0xE1,0x00,0x00,0x45,0x78,0x69,0x66,0x00,0x00,
    0x49,0x49,0x2A,0x00,0x08,0x00,0x00,0x00,0x01,0x00,0x25,0x88,
    0x04,0x00,0x01,0x00,0x00,0x00,0x1A,0x00,0x00,0x00,0x01,0x00,
    0x01,0x00,0x02,0x00,0x02,0x00,0x00,0x00,0x41,0x00,0x00,0x00,
    0xFF,0xFF,0xFF,0xFF,0xFF,0xD9
])

def test(tag, jpeg):
    jpeg = bytearray(jpeg)
    jpeg[4:6] = struct.pack(">H", len(jpeg)-2)
    open("t.jpg","wb").write(jpeg)
    print("TEST "+tag, flush=True)
    url = cf.CFURLCreateFromFileSystemRepresentation(None, b"t.jpg", 5, False)
    if not url: print("  no url"); return
    src = imgio.CGImageSourceCreateWithURL(url, None)
    cf.CFRelease(url)
    if not src: print("  no source"); return
    props = imgio.CGImageSourceCopyPropertiesAtIndex(src, 0, None)
    cf.CFRelease(src)
    if not props: print("  no props"); return
    n = cf.CFDictionaryGetCount(props)
    print("  DICT COUNT = "+str(n), flush=True)
    cf.CFRelease(props)

for off in [0x10,0x40,0x100,0x400,0x1000,0x4000,0x10000,0x40000,0x100000,0x7FFFFFF0]:
    j = bytearray(base); j[48:52] = struct.pack("<I", off)
    test("nextIFD=0x%x"%off, j)
for cnt in [0x0100,0x1000,0x8000,0xFFFF]:
    j = bytearray(base); j[20:22] = struct.pack("<H", cnt)
    test("ifd0count=0x%x"%cnt, j)
for cnt in [0x00010000,0x40000000,0xFFFFFFFF]:
    j = bytearray(base); j[40:44] = struct.pack("<I", cnt)
    test("gpscount=0x%x"%cnt, j)
print("DONE", flush=True)
