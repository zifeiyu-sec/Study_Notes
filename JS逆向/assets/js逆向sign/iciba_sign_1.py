import hashlib

def calculate_md5_sign(input_str):
    # 计算 MD5（32位 hex）
    md5_hash = hashlib.md5(input_str.encode("utf-8")).hexdigest()
    # 截取前 16 位
    return md5_hash[:16]

# 示例
input_str = "6key_web_new_fanyi6dVjYLFyzfkFkk傻逼"
sign = calculate_md5_sign(input_str)
print(sign)  # 输出：前 16 位 MD5
