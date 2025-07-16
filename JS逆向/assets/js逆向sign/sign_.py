import hashlib
import time

def generate_sign(url, cookie_uu):
    """
    生成 sign 参数
    
    参数:
        url: API 路径，例如 '/api/banner/get'
        cookie_uu: cookie 中的 uu 值
        
    返回:
        sign 字符串
    """
    o = "12b6bb84e093532fb72b4d65fec3f00b"
    n = str(int(time.time() * 1000))  # 当前时间戳，毫秒级
    r = url.replace("/api", "")  # 去掉 /api 部分
    c = cookie_uu
    
    # 拼接字符串: o + c + r + n + o
    sign_str = o + c + r + n + o
    
    # MD5 加密
    m = hashlib.md5()
    m.update(sign_str.encode('utf-8'))
    sign = m.hexdigest()
    
    return sign

# 示例使用
if __name__ == "__main__":
    url = "/api/banner/get"
    cookie_uu = "e9ffc306-738b-4752-81ed-8e484140c74e"  # 替换为实际的 cookie uu 值
    
    sign = generate_sign(url, cookie_uu)
    print(f"Generated Sign: {sign}")
    print(f"Timestamp: {int(time.time() * 1000)}")