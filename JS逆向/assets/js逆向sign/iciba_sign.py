import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def calculate_md5_sign(input_str):
    """计算输入字符串的 MD5，并返回前 16 位 hex"""
    md5_hash = hashlib.md5(input_str.encode("utf-8")).hexdigest()
    return md5_hash[:16]

def aes_encrypt(plaintext, key="L4fBtD5fLC9FQw22"):
    """AES-ECB 加密，返回 Base64 结果"""
    key_bytes = key.encode("utf-8")
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    padded_data = pad(plaintext.encode("utf-8"), AES.block_size, style="pkcs7")
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode("utf-8")

def combined_sign(base_str, dynamic_part):
    """
    组合签名计算：
    1. 拼接 base_str + dynamic_part
    2. 计算 MD5 前 16 位
    3. 进行 AES 加密
    """
    full_input = base_str + dynamic_part
    md5_16 = calculate_md5_sign(full_input)
    encrypted_result = aes_encrypt(md5_16)
    return encrypted_result

def interactive_test():
    """交互式测试，动态输入 '傻逼' 部分并输出加密结果"""
    base_str = "6key_web_new_fanyi6dVjYLFyzfkFkk"  # 固定前缀
    while True:
        dynamic_part = input("请输入动态部分（输入 'exit' 退出）: ").strip()
        if dynamic_part.lower() == "exit":
            break
        encrypted = combined_sign(base_str, dynamic_part)
        print(f"输入: {dynamic_part} | 加密结果: {encrypted}")

if __name__ == "__main__":
    print("===== 动态加密测试 =====")
    print("固定部分: '6key_web_new_fanyi6dVjYLFyzfkFkk'")
    print("动态部分: 由用户输入（原代码中的 '傻逼' 位置）")
    interactive_test()