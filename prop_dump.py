import sys, ctypes, ctypes.util
out = open("plog.txt","a")
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

fn = sys.argv[1].encode()
log("FILE "+fn.decode())
url = cf.CFURLCreateFromFileSystemRepresentation(None, fn, len(fn), False)
src = imgio.CGImageSourceCreateWithURL(url, None)
cf.CFRelease(url)
if not src:
    log("  no source"); out.close(); sys.exit(0)
props = imgio.CGImageSourceCopyPropertiesAtIndex(src, 0, None)
if not props:
    log("  no props")
else:
    log("  DICT COUNT = "+str(cf.CFDictionaryGetCount(props)))
    cf.CFRelease(props)
cf.CFRelease(src)
log("  OK")
out.close()
