import sys
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

old_pw = '12346'
attr = {
    'iv': '187cbe6b30d64549b01992f227afe0ea',
    'pw': 'bf24abfc31c6709660d34c0f3afc47b88c3136094ab58e61c8a756d9b0fc943b9d30e409588ea7b2fb8cf5e22c89900c278850f47aac141acfd4c6d1420009b1',
    'cs': 'a821906e68275dbd22fc10f97fe690e3'
}

m = hashlib.md5()
m.update(old_pw.encode('utf-8'))
key_plain = m.hexdigest().lower()
key = bytes.fromhex(key_plain)
iv = bytes.fromhex(attr['iv'])
text = bytes.fromhex(attr['pw'])

m = hashlib.md5()
m.update(key_plain.encode('utf-8'))
m.update(attr['iv'].encode('utf-8'))
m.update(attr['pw'].encode('utf-8'))
if m.hexdigest().lower() == attr['cs']:
    print('checksum matches')
else:
    print('mismatch in checksum. aborting...')
    sys.exit(1)

cipher = AES.new(key, AES.MODE_CBC, iv)
pt = unpad(cipher.decrypt(text), AES.block_size)

print(pt)
