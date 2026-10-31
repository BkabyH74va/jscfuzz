import struct, random, ctypes, ctypes.util

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

base = bytearray([
    0xFF,0xD8,0xFF,0xE1,0x00,0x00,0x45,0x78,0x69,0x66,0x00,0x00,
    0x49,0x49,0x2A,0x00,0x08,0x00,0x00,0x00,0x01,0x00,0x25,0x88,
    0x04,0x00,0x01,0x00,0x00,0x00,0x1A,0x00,0x00,0x00,0x01,0x00,
    0x01,0x00,0x02,0x00,0x02,0x00,0x00,0x00,0x41,0x00,0x00,0x00,
    0xFF,0xFF,0xFF,0xFF,0xFF,0xD9
])

count = 0
while True:
    count += 1
    if count % 500 == 0:
        with open("mutlog.txt","a") as f: f.write("Tested %d\n" % count)
    jpeg = bytearray(base)
    for i in range(34, 48):
        if random.random() < 0.35:
            jpeg[i] = random.choice([0x00,0xFF,0x41,0x7F,0x01,0x10,random.randint(0,255)])
    jpeg[4:6] = struct.pack(">H", len(jpeg)-2)
    open("seed.jpg","wb").write(jpeg)
    url = cf.CFURLCreateFromFileSystemRepresentation(None, b"seed.jpg", 8, False)
    if url:
        src = imgio.CGImageSourceCreateWithURL(url, None)
        cf.CFRelease(url)
        if src:
            props = imgio.CGImageSourceCopyPropertiesAtIndex(src, 0, None)
            if props:
                n = cf.CFDictionaryGetCount(props)
                if n > 100:
                    with open("mutlog.txt","a") as f: f.write("BIGDICT %d at %d\n" % (n, count))
                cf.CFRelease(props)
            cf.CFRelease(src)
