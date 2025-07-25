import requests

if __name__ == '__main__':
    js_code="""
   console.log('hello world')
  """
    url="http://127.0.0.1:12080/execjs"
    data={
        "group":"xiaodi",
        "code":js_code
    }
    res=requests.post(url,data=data)
