import os, ctypes, ctypes.util
out = open("plog.txt","w")
def log(m):
    out.write(m+"\n"); out.flush()

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

files = sorted(f for f in os.listdir(".") if f.endswith(".jpg"))
log("FILES: "+", ".join(files))
for fn in files:
    log("FILE "+fn)
    fne = fn.encode()
    url = cf.CFURLCreateFromFileSystemRepresentation(None, fne, len(fne), False)
    src = imgio.CGImageSourceCreateWithURL(url, None)
    cf.CFRelease(url)
    if not src:
        log("  no source"); continue
    props = imgio.CGImageSourceCopyPropertiesAtIndex(src, 0, None)
    cf.CFRelease(src)
    if not props:
        log("  no props"); continue
    n = cf.CFDictionaryGetCount(props)
    log("  DICT COUNT = "+str(n))
    cf.CFRelease(props)
log("DONE")
out.close()
