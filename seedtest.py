import sys, ctypes, ctypes.util
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
url = cf.CFURLCreateFromFileSystemRepresentation(None, fn, len(fn), False)
src = imgio.CGImageSourceCreateWithURL(url, None)
cf.CFRelease(url)
props = imgio.CGImageSourceCopyPropertiesAtIndex(src, 0, None)
n = cf.CFDictionaryGetCount(props) if props else -1
print("SURVIVED count="+str(n), flush=True)
if props: cf.CFRelease(props)
cf.CFRelease(src)
