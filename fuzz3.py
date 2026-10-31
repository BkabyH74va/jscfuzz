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
cf.CFDictionaryGetKeysAndValues.restype = None
cf.CFDictionaryGetKeysAndValues.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
cf.CFStringGetCString.restype = ctypes.c_bool
cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32]
cf.CFGetTypeID.restype = ctypes.c_ulong
cf.CFGetTypeID.argtypes = [ctypes.c_void_p]
cf.CFDictionaryGetTypeID.restype = ctypes.c_ulong
cf.CFRelease.restype = None
cf.CFRelease.argtypes = [ctypes.c_void_p]
DICTTYPE = cf.CFDictionaryGetTypeID()

print("START", flush=True)

REAL = base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDwKiiivzI/uM//2Q==")

def exif_block(nextIFD, gpsCount, gpsRefVal, userCount, userVal):
    t = bytearray([0x49,0x49,0x2A,0x00,0x08,0x00,0x00,0x00])
    t += struct.pack("<H", 2)
    t += struct.pack("<HHII", 0x8769, 4, 1, 0x50)   # ExifIFD -> 0x50
    t += struct.pack("<HHII", 0x8825, 4, 1, 0x80)   # GPSInfo -> 0x80
    t += struct.pack("<I", nextIFD)                  # next IFD (corruptable)
    while len(t) < 0x50: t += b"\x00"
    t += struct.pack("<H", 2)
    t += struct.pack("<HHII", 0x9000, 7, 4, 0x31333230)  # ExifVersion "0231"
    t += struct.pack("<HHII", 0x9286, 7, userCount, userVal) # UserComment (corrupt)
    t += struct.pack("<I", 0)
    while len(t) < 0x80: t += b"\x00"
    t += struct.pack("<H", 2)
    t += struct.pack("<HHII", 0x0000, 1, 4, 0x00000302)    # GPSVersionID 2.3.0.0
    t += struct.pack("<HHII", 0x0002, 2, gpsCount, gpsRefVal) # GPSLatitudeRef (corrupt)
    t += struct.pack("<I", 0)
    app1 = bytes([0x45,0x78,0x69,0x66,0x00,0x00]) + bytes(t)
    seg = bytearray([0xFF,0xE1]) + struct.pack(">H", len(app1)+2) + app1
    return REAL[:2] + bytes(seg) + REAL[2:]

def cfstr(p):
    buf = ctypes.create_string_buffer(200)
    if cf.CFStringGetCString(p, buf, 200, 0x08000100):
        return buf.value.decode('utf-8','replace')
    return "<?>"

def walk(d, depth, lines):
    n = cf.CFDictionaryGetCount(d)
    lines.append("  "*depth + "count=" + str(n))
    if depth >= 2 or n < 1 or n > 400: return
    keys = (ctypes.c_void_p * n)()
    vals = (ctypes.c_void_p * n)()
    cf.CFDictionaryGetKeysAndValues(d, keys, vals)
    for i in range(n):
        k = cfstr(keys[i])
        if cf.CFGetTypeID(vals[i]) == DICTTYPE:
            lines.append("  "*depth + k + " ->")
            walk(vals[i], depth+1, lines)
        else:
            lines.append("  "*depth + k)

def test(tag, data):
    open("t.jpg","wb").write(data)
    print("TEST "+tag, flush=True)
    url = cf.CFURLCreateFromFileSystemRepresentation(None, b"t.jpg", 5, False)
    src = imgio.CGImageSourceCreateWithURL(url, None)
    cf.CFRelease(url)
    if not src: print("  no source"); return
    props = imgio.CGImageSourceCopyPropertiesAtIndex(src, 0, None)
    cf.CFRelease(src)
    if not props: print("  no props"); return
    lines = []
    walk(props, 0, lines)
    for L in lines[:50]: print("  "+L, flush=True)
    cf.CFRelease(props)

test("baseline", exif_block(0, 2, 0x41, 8, 0x99))
test("nextIFD=0x10", exif_block(0x10, 2, 0x41, 8, 0x99))
test("nextIFD=0x1000", exif_block(0x1000, 2, 0x41, 8, 0x99))
test("nextIFD=0xffffffff", exif_block(0xFFFFFFFF, 2, 0x41, 8, 0x99))
test("gpscount=0xffffffff", exif_block(0, 0xFFFFFFFF, 0xA0, 8, 0x99))
test("gpscount=0x10000-ref0x1000", exif_block(0, 0x10000, 0x1000, 8, 0x99))
test("usercount=0xffffffff", exif_block(0, 2, 0x41, 0xFFFFFFFF, 0x1000))
test("usercount=0x40000000", exif_block(0, 2, 0x41, 0x40000000, 0x1000))
print("DONE", flush=True)
