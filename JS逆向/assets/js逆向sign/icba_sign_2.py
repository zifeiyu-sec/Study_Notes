from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def encrypt_string(e, t="%5C%C2%80%C2%9A%C2%A8%C2%B6%C2%B8y%C2%9B%C2%B2%C2%8F%7C%7F%C2%97%C3%88%C2%A9d"):
    # 密钥处理 - 与JS代码中的处理一致
    key = "L4fBtD5fLC9FQw22".encode('utf-8')
    
    # 加密数据
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = pad(e.encode('utf-8'), AES.block_size, style='pkcs7')
    encrypted = cipher.encrypt(padded_data)
    
    return base64.b64encode(encrypted).decode('utf-8')

# 测试
plaintext = "fd13c4cb1a51fd2e"
result = encrypt_string(plaintext)
print(result)