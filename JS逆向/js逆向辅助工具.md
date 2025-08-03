# v-jstools

项目地址：https://github.com/Zjingwen/v-jstools

## 安装

下载项目后，打开浏览器开发者模式

将工具添加进去。

## 配置

![image-20250723223607130](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723223607130.png)

![image-20250723223632825](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723223632825.png)

![image-20250723223639535](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723223639535.png)

按照自己需求配置后就可以使用了

## 使用

逆向目标靶场

http://39.98.108.20:8085/#/user

打开开发者工具

控制台可以看到下面字样，说明工具启动成功

![image-20250723223903451](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723223903451.png)

随便输入账号密码进行测试

![](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723223746484.png)

查看数据包

![image-20250723224032007](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224032007.png)

可以看到输入的数据被加密了

如果没有这款工具，就是常规的，断点调试，一步步分析，但有这个插件，可以直接查看控制台

![image-20250723224234370](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224234370.png)

可以看到工具直接给标注了出来

点击进去

![image-20250723224303610](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224303610.png)

然后进行断点调试

大致观察后在if处进行断点

![image-20250723224339660](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224339660.png)

重新点击登录，查看断点处

![image-20250723224413779](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224413779.png)

分析

![image-20250723224603570](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224603570.png)

所有加密发生在`l()`函数中，定位进去分析

![image-20250723224802124](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723224802124-1753282082508-1.png)

点击进去后看到加密过程

> - AES加密函数，接收明文`t`作为参数
> - `f`是加密密钥，使用UTF-8编码将字符串"1234567891234567"转换为字节数组
> - `h`是初始化向量(IV)，与密钥相同
> - 使用CBC模式(Cipher Block Chaining)
> - 使用PKCS7填充方案
> - 返回加密后的Base64格式字符串
> - 密钥长度：16字节(128位)，因为"1234567891234567"是16个字符

成功逆向到加密处理过程。

测试是否分析正确

打开加密工具

![image-20250723225644401](./js%E9%80%86%E5%90%91%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE.assets/image-20250723225644401.png)

按照分析结

果填充值，查看结果，很明显，和数据包中结果一致，成功逆向到加密，对于返回数据包的解密，也是同样方式

==对于这个工具，不使用的时候关闭，负责影响加载速度==



# autoDecode

项目网址：https://github.com/f0ng/autoDecoder/tree/0.54

burp插件





# JSRpc

https://github.com/jxhczhl/JsRpc

使用教程：https://mp.weixin.qq.com/s/vHoVPINf4GKhR36LSQlDXw

流程

1、植入JSEnv并启动ws服务端

执行：resouces/JsEnv_Dev.js

执行：window_amd64.exe

 

2、本地替换加密函数JS文件

添加连接JSRPC和注册接口并调用加密

//连接JSRPC

var demo = new Hlclient("ws://127.0.0.1:12080/ws?group=xiaodi&name=xiaodisec");

//注册接口并调用加密

demo.regAction("pass",function(resolve,param){

​	resolve(l(param));

})

3、访问注册接口测试加密

http://127.0.0.1:12080/go?group=xiaodi&name=xiaodisec&action=pass&param=123456

# 联动

目标站点：https://passport.meituan.com/account/unitivelogin?_nsmobilelogin=true

## 定位加密的位置

进行登录

![image-20250729134450246](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729134450246.png)

定位到数据包

![image-20250729134526962](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729134526962.png)

查看启动器

![image-20250729134603572](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729134603572.png)

猜测加密可能发生的位置，点击进入文件，任意打一个断点进行查看

![image-20250729151143925](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729151143925.png)

密码已经被加密了，查看前面调用的堆栈或者当前代码前面部分

断点向前调整，

![image-20250729151312156](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729151312156.png)

密码还是被加密的，继续往前查看

找到了密码加密的位置

![image-20250729151439544](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729151439544.png)

控制台测试

![image-20250729151826150](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729151826150-1753773506479-1.png)



成功逆向到密码加密的位置

## 使用JSRpc

启动jsrpc

![image-20250729152130602](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729152130602-1753773701995-4.png)



将当前项目resources目录下

![image-20250729152233991](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729152233991.png)

文件中的代码粘贴到浏览器控制台

回到刚才定位到的加密的位置

![image-20250729152418596](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729152418596.png)

替换内容到本地，添加下面代码

```
var demo = new Hlclient("ws://127.0.0.1:12080/ws?group=xiaodi&name=xiaodisec");

        demo.regAction("pass",function(resolve,param){
    	resolve(encrypt.encrypt(param));
        })
        
        group=xiaodi&name=xiaodisec这些参数后续调用接口会使用
        encrypt.encrypt 是原本脚本使用的加密函数，
```

修改内容

![image-20250729152610096](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729152610096.png)

修改后保存，然后重新弄登录来加载文件

可以看到重新调用加载了我们刚刚在控制台和替换内容中插入的脚本，

![image-20250729152913065](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729152913065.png)



访问呢接口

> http://127.0.0.1:12080/go?group=xiaodi&name=xiaodisec&action=pass&param=123456
>
> 123456就是要加密的值

![image-20250729153011455](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729153011455.png)

## 联动autoDecode插件

### 配置插件

打开burp进行autodecode插件的配置

![image-20250729153523053](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729153523053-1753774523717-8.png)

### 配置脚本

打开autodecode项目

![image-20250729222955007](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729222955007.png)

这两个脚本就是我们需要配置的脚本的模板

按照这两个脚本进行配置

```py
import requests
import json
from urllib.parse import quote
from flask import Flask, request

app = Flask(__name__)  
url = "http://localhost:12080/go"
@app.route('/encode',methods=["POST"])  
def encrypt():  
    param = request.form.get('dataBody')  # 获取  post 参数  
    #print(json.dumps(param))
    param_headers = request.form.get('dataHeaders')  # 获取  post 参数  
    param_requestorresponse = request.form.get('requestorresponse')  # 获取  post 参数  
    data = {
        "group": "xiaodi",
        "name": "xiaodisec",
        "action": "pass",
        "param": json.dumps(param)
    }
    res = requests.post(url, data=data) #这里换get也是可以的
    encry_param = json.loads(res.text)['data']
    print(encry_param)
    if param_requestorresponse == "request":  
        return param_headers + "\r\n\r\n\r\n\r\n" + encry_param  
    return encry_param

@app.route('/decode',methods=["POST"])  
def decrypt():  
    param = request.form.get('dataBody')  # 获取  post 参数  
    param_headers = request.form.get('dataHeaders')  # 获取  post 参数  
    param_requestorresponse = request.form.get('requestorresponse')  # 获取  post 参数  
    print(param)
    data = {
        "group": "xiaodi",
        "name": "xiaodisec",
        "action": "dec",
        "param": param
    }
    res = requests.post(url, data=data) #这里换get也是可以的
    decrypt_param = json.loads(res.text)['data']
    print(decrypt_param)
    if param_requestorresponse == "request":  
        return param_headers + "\r\n\r\n\r\n\r\n" + decrypt_param  
    else:  
        return decrypt_param  

if __name__ == '__main__':  
    app.debug = True # 设置调试模式，生产模式的时候要关掉debug  
    app.run(host="0.0.0.0",port="8888")
```

配置好脚本后运行

![image-20250729223257452](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729223257452.png)

访问本地链接

![image-20250729223341589](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729223341589.png)

看到这样说明脚本运行成功

访问在autodecode插件中配置的接口

http://192.168.1.5:8888/encode

即在刚才访问路径的后面添加/encode

对这个数据包进行抓包，然后修改请求为post

![image-20250729223649006](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729223649006.png)

然后按照脚本中![image-20250729223729442](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729223729442.png)

dataBody就是传入传入参数的位置，我们传入参数，后面的值就是我们要加密的值，这个脚本会调用jsrpc中前面配置加密的脚本，并且获取到加密值

![image-20250729223907233](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729223907233.png)

发送请求

![image-20250729223928278](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729223928278.png)

成功返回加密后的值，调用成功

### 测试

接下来进行测试

抓取前面页面登录的数据包

![image-20250729224108738](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729224108738.png)

![image-20250729224139480](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729224139480.png)

发送到爆破模块

![image-20250729224213170](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729224213170.png)

配置爆破字典

![image-20250729224305101](./images/js%E9%80%86%E5%90%91%E8%BE%85%E5%8A%A9%E5%B7%A5%E5%85%B7/image-20250729224305101.png)

记得插件中配置只对password进行加密，不配置的话会对整个数据加密

然后就可以执行爆破了，成功复现了一次，但是再次复习发现没法实现加密，根据报错是传参错误



