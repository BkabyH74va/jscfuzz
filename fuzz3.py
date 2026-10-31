import sys
sys.stdout = open("log.txt","w")
sys.stderr = sys.stdout
import struct, ctypes, ctypes.util, base64

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

REAL = base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDwKiiivzI/uM//2Q==")

def with_exif(nextIFD, gpsCount, ifd0count):
    t = bytearray([0x49,0x49,0x2A,0x00,0x08,0x00,0x00,0x00])
    t += struct.pack("<H", ifd0count)
    t += struct.pack("<HHII", 0x8825, 4, 1, 0x1A)
    t += struct.pack("<I", nextIFD)
    while len(t) < 0x1A: t += b"\x00"
    t += struct.pack("<H", 1)
    t += struct.pack("<HHI", 0x0002, 2, gpsCount)
    t += struct.pack("<I", 0x41)
    app1 = bytes([0x45,0x78,0x69,0x66,0x00,0x00]) + bytes(t)
    seg = bytearray([0xFF,0xE1]) + struct.pack(">H", len(app1)+2) + app1
    return REAL[:2] + bytes(seg) + REAL[2:]

def test(tag, data):
    open("t.jpg","wb").write(data)
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

test("baseline-plain", REAL)
test("baseline-exif", with_exif(0, 2, 1))
for off in [0x10,0x100,0x1000,0x10000,0x100000,0x7FFFFFF0,0xFFFFFFFF]:
    test("nextIFD=0x%x"%off, with_exif(off, 2, 1))
for cnt in [0x0100,0x1000,0x8000,0xFFFF]:
    test("ifd0count=0x%x"%cnt, with_exif(0, 2, cnt))
for cnt in [0x10000,0x40000000,0xFFFFFFFF]:
    test("gpscount=0x%x"%cnt, with_exif(0, cnt, 1))
print("DONE", flush=True)
