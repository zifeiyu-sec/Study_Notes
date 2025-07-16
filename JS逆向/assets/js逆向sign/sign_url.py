import hashlib
import time
import requests
import json
import uuid

def generate_sign(url, uu_cookie, timestamp=None):
    """
    生成 sign 参数
    
    参数:
        url (str): 请求的URL (例如 '/api/questions/lists')
        uu_cookie (str): cookies中的'uu'值
        timestamp (str, optional): 可选的时间戳，如果不提供则使用当前时间
        
    返回:
        dict: 包含 sign 和时间戳 timestamp 的字典
    """
    # 固定值 o
    o = "12b6bb84e093532fb72b4d65fec3f00b"
    # 时间戳 timestamp
    timestamp = timestamp or str(int(time.time() * 1000))
    # 处理URL r
    r = url.replace("/api", "")
    # uu cookie值 c
    c = uu_cookie
    
    # 拼接字符串
    concatenated = o + c + r + timestamp + o
    # MD5加密
    sign = hashlib.md5(concatenated.encode('utf-8')).hexdigest()
    
    return {
        'sign': sign,
        'timestamp': timestamp
    }

def make_request():
    # 请求URL
    url = "https://www.kaoshibao.com/api/questions/lists"
    
    # 从cookie中提取的uu值
    uu_cookie = "e9ffc306-738b-4752-81ed-8e484140c74e"
    
    # 生成sign和时间戳
    sign_data = generate_sign("/api/questions/lists", uu_cookie)
    
    # 生成新的request-id
    request_id = str(uuid.uuid4())
    
    # 请求头
    headers = {
        'authority': 'www.kaoshibao.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'client-identifier': uu_cookie,  # 使用uu_cookie作为client-identifier
        'content-type': 'application/json;charset=UTF-8',
        'cookie': f'UM_distinctid=1980cdeeb2f1243-05df1e0e2b857f-4c657b58-232800-1980cdeeb301807; uu={uu_cookie}; Hm_lvt_975400bd703f587eef8de1efe396089d=1752562592,1752586822; HMACCOUNT=0321B88F336C73D8; CNZZDATA1278923901=1938137518-1752562593-%7C1752586828; Hm_lpvt_975400bd703f587eef8de1efe396089d=1752586828',
        'origin': 'https://www.kaoshibao.com',
        'platform': 'web',
        'pragma': 'no-cache',
        'referer': 'https://www.kaoshibao.com/online/paper/detail/?paperid=23151209',
        'request-id': request_id,
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="137", "Edge";v="137"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sign': sign_data['sign'],
        'timestamp': sign_data['timestamp'],
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        'version': '2.4.2'
    }
    
    # 请求体
    payload = {
        "paperid": "23151209",
        "type": "all",
        "size": 10,
        "page": 1
    }
    
    try:
        # 发送POST请求
        response = requests.post(
            url,
            headers=headers,
            json=payload,  # 使用json参数自动序列化并设置Content-Type
            verify=True  # 保持SSL验证开启
        )
        
        # 检查响应状态
        if response.status_code == 200:
            print("请求成功！")
            print("响应内容:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except ValueError:
                print(response.text)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None

if __name__ == "__main__":
    response = make_request()