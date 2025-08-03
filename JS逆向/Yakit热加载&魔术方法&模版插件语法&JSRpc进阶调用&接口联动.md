# JS逆向-安全辅助项目&Yakit热加载&魔术方法&模版插件语法&JSRpc进阶调用&接口联动

## Yakit热加载

参考：https://yaklang.com/products/Web%20Fuzzer/fuzz-hotpatch/

> Yakit的热加载(Hot Reload)功能允许开发者在不重启应用的情况下动态更新代码和插件，主要特点包括：
>
> 1. **即时生效**：修改代码后立即应用变更，无需重启Yakit
> 2. **插件开发**：特别适合插件开发时的快速迭代测试
> 3. **多种支持**：
>    - 脚本热加载
>    - 插件模块热更新
>    - UI界面实时刷新
> 4. **使用方式**：
>    - 通过`Ctrl+S`保存文件触发热加载
>    - 使用Yakit专用热加载API
> 5. **优势**：大幅提升开发效率，减少测试等待时间
>
> 热加载是Yakit为安全研究人员和开发者提供的高效开发体验核心功能之一。

## Yak脚本

> Yak 是一种专门为网络安全测试设计的编程语言，而 **Yak 脚本** 就是使用这种语言编写的程序。它们就像是一系列指令，告诉计算机去执行特定的任务。例如，你可以写一个脚本来自动测试某个网站是否存在常见的安全漏洞，或者模拟攻击以验证防御措施的有效性。
>
> ### 主要特点
>
> 1. **专门针对网络安全**：Yak 脚本提供了丰富的库和函数，使得编写与网络安全相关的任务变得简单。无论是端口扫描、漏洞检测还是数据加密，都能轻松实现。
> 2. **易于学习**：对于已经熟悉编程的人来说，Yak 的语法相对直观，容易上手。即使你是初学者，也可以通过官方文档和示例快速入门。
> 3. **热加载支持**：在开发过程中，你可以利用热加载功能实时查看代码修改后的效果，无需重启整个环境，大大提高了效率。
> 4. **集成能力强**：Yak 可以与其他工具（如 Burp Suite）无缝集成，增强其功能，满足更复杂的安全测试需求。
>
> ### 简单例子
>
> 假设你想检查一个网站是否对 SQL 注入攻击敏感，可以编写如下简单的 Yak 脚本：
>
> ```
> site = "http://example.com/login"
> 
> // 构造可能引起SQL注入的输入
> payload = "' OR '1'='1"
> 
> // 发送包含payload的请求
> response = http.Post(site, f`username=${payload}&password=anything`)
> 
> // 检查响应中是否包含特定内容，表明可能存在漏洞
> if strings.Contains(response.Body(), "Welcome") {
>     log.info("Potential SQL Injection vulnerability detected!")
> }
> ```
>
> 这段脚本首先构造了一个可能会触发 SQL 注入的特殊字符串 `payload`，然后将这个字符串作为用户名参数的一部分发送给目标网站，并根据服务器返回的内容判断该网站是否可能存在 SQL 注入的风险。
>
> 总之，Yak 脚本就像是你的私人网络安全助手，帮助你自动化执行复杂的任务，发现潜在的问题，并确保网络环境更加安全。无论你是专业的安全研究人员，还是对此领域感兴趣的爱好者，Yak 都是一个非常强大的工具。

打开yakit后选择临时项目进行界面，简单了解yak脚本![image-20250731151635147](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731151635147.png)

![image-20250731152228885](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152228885.png)

# 案列

## 案列一

### 开启靶场

![image-20250731152422472](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152422472.png)

![image-20250731152436126](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152436126.png)

![image-20250731152506532](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152506532.png)

开启失败可能端口占用，换一个端口试试

### 开启劫持

![image-20250731152621323](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152621323.png)

![image-20250731152653980](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152653980.png)

在启动的浏览器中当问刚才开启的靶场

http://127.0.0.1:8787/

选择这个靶场

![image-20250731152756318](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152756318.png)

### js逆向sign加密分析

输入数据测试，发现signature被加密

![image-20250731152954388](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731152954388.png)

逆向分析签名的加密方法，已经在一开始的js逆向中介绍过，只做个大概

![image-20250731153114978](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731153114978.png)

![image-20250731150359048](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731153242099.png)

断点调试

![image-20250731153341489](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731153341489.png)

word的值：username=admin&password=123456

定位Encrypt()函数

> **使用 HMAC-SHA256 算法，对输入的字符串 `word` 进行加密，并返回加密后的结果**。
>
> 可拆分为 3 步：
>
> 1. `key.toString(CryptoJS.enc.Utf8)`：将加密密钥 `key` 转换为 UTF-8 编码格式（确保密钥格式符合 CryptoJS 的要求）。
> 2. `CryptoJS.HmacSHA256(word, ...)`：调用 CryptoJS 库的 HMAC-SHA256 算法，用处理后的密钥对 `word` 进行加密计算，得到一个加密对象。
> 3. `.toString()`：将加密对象转换为字符串形式（通常是十六进制字符串），作为最终的加密结果返回。

![image-20250731153447612](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731153447612.png)

可以看到`k`,查看key，从函数generateKey()得到

![image-20250731153546132](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731153546132.png)

追踪k的值，发现k是1234123412341234的ascii码的十六进制

成功逆向到js中sign的加密方法。验证一下

![image-20250731154108821](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154108821.png)

与数据包中的signature结果一致，成功逆向。

### yakit结合热加载爆破

劫持登录的数据包

![image-20250731154248390](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154248390.png)

![image-20250731154308282](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154308282.png)

![image-20250731154410783](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154410783.png)



```yak
func sign(user, pass) {
    return codec.EncodeToHex(codec.HmacSha256("1234123412341234", f`username=${user}&password=${pass}`)~)
}

signRequest = result => {
    pairs := result.SplitN("|", 2)
    dump(pairs)
    return sign(pairs[0], pairs[1])
}
```

> 调用：{{yak(signRequest|admin|{{x(pass_top25)}})}}



![image-20250731154421255](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154421255.png)



![image-20250731154914655](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154914655.png)

​	![image-20250731154956629](./images/%E5%AE%89%E5%85%A8%E8%BE%85%E5%8A%A9%E9%A1%B9%E7%9B%AE&Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250731154956629.png)

签名验证成功！！

## 案列二

还是案例一中的靶场

![image-20250801164623446](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250801164623446.png)

发送数据包的载荷

![image-20250801164704309](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250801164704309.png)

逆向到的加密算法

> ==AES-CBC 模式，PKCS7填充==
>
> 初始向量iv:随机生成
>
> key:12341234123412324(utf-8)
>
> 加密数据：{"username":"niuma","password":"123456"}
>
> 加密结果（base64处理）：+zQp3V6b2oHoL7aqLx88tmi78RTDi41Q6U7ONKyb1kJd/g5N4qWgD5h9xK7hl9mB
>
> 最终发送的数据包的数据：
>
> {
>
>  **"data"**: **"+zQp3V6b2oHoL7aqLx88tmi78RTDi41Q6U7ONKyb1kJd/g5N4qWgD5h9xK7hl9mB"**,
>
>  **"key"**: **"31323334313233343132333431323334"**,
>
>  **"iv"**: **"0bd776371592ea53182c2ad3f5a6add2"**
>
> }



验证加密：

![image-20250802182932899](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250802182932899.png)

成功逆向加密逻辑，接下来在yakit中配置热加载：

抓取数据包发送发哦web fuzzer模块

![image-20250802183119110](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250802183119110.png)

打开热加载，配置如下yak代码

```yak
aescbc = result => {
    result = codec.AESCBCEncryptWithPKCS7Padding(
        codec.DecodeHex(`31323334313233343132333431323334`)~,
        result,
        codec.DecodeHex(`bfeb9fdf041beaa31a1f136700f5e25c`)~,
    )~
    return string(result)
}
```

> ### 功能概述：
>
> 定义一个名为 `aescbc` 的函数，作用是：
>
> - 使用 **AES-CBC 模式 + PKCS7 填充** 对输入的 `result` 数据进行加密。
> - 使用固定的 **密钥（Key）** 和 **初始化向量（IV）**。
> - 返回加密后的密文（二进制数据转为字符串）。

> - `31323334313233343132333431323334` 是十六进制字符串。
> - 转成 ASCII 字符串是：`1234123412341234`（共 16 字节 → 128 位）
> - 这是 **AES-128 的密钥（Key）**。
> - `~` 是 Yak 的 **强制解引用操作符**，确保返回原始字节。
>
> ✅ 等价于：`key = "1234123412341234"`

==调用:**{{base64(**{{yak(aescbc|{"username":"admin","password":"*{{x(*pass_top25)}}"})}})}}==

```
1. 从字典取出密码 → {{x(pass_top25)}}
2. 构造登录数据     → {"username":"admin","password":"123456"}
3. 调用 Yak 函数     → aescbc(json)
   └─ 使用固定 Key 和 IV 进行 AES-CBC 加密
4. 得到二进制密文    → \x1a\x2b\x3c...
5. Base64 编码       → "GisrPA==..."
6. 插入到 HTTP 请求中
```

配置后保存模板，然后在数据包中调用

![image-20250802183754175](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250802183754175.png)

==注意iv必须和热加载使用的一样，负责会错误==，我此处没有同步，发生错误

![image-20250802185216380](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250802185216380.png)

修改iv后进行爆破，可以爆破了

## 案列三--结合jsrpc以及魔术方法

靶场：http://121.43.105.51:82/

### 逆向js

根据js_tools工具或者其他方式定位到加密的js文件，防线被混淆，利用ai对混淆的代码还原

![image-20250802194434310](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250802194434310.png)

最终得到：

> 加密方式:AES，CBC模式
>
> iv和key一致：1234567890123456
>
> 用户：testuser
>
> 密码：TestPass123!
>
> 加密的数据：{"username":"testuser","password":"TestPass123!"}
>
> 数据包载荷：Y0g6b26ua/JSzlMPhwmYiCYYVo9JEZokhGx0IkdSutrVAXSBncCSBkr0RjX247q2Ss1jNYykywD8Ux/4pkXnkw==

验证：

![image-20250802194244813](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250802194244813.png)



成功逆向

### 启动连接JSRpc

启动jsrpc并连接。

> var demo = new Hlclient("ws://127.0.0.1:12080/ws?group=zzz");



> 由于不能内容替换，将原来的加密逻辑封装在控制台
>
> //encrypts_aes 函数
> function encrypts_aes(data) {
>     const input = String(data);
>     
>
>     // 正常AES加密逻辑（使用CryptoJS）
>     const key = CryptoJS.enc.Utf8.parse('1234567890123456'); // 16位密钥
>     const iv = CryptoJS.enc.Utf8.parse('1234567890123456');  // 16位向量
>     const encrypted = CryptoJS.AES.encrypt(input, key, {
>         iv: iv,
>         mode: CryptoJS.mode.CBC,
>         padding: CryptoJS.pad.Pkcs7
>     }).toString(); // 转为Base64结果
>     
>     return encrypted;
> }
>
> 注册函数联合jsrpc调用
> demo.regAction("decrypt", function (resolve, param) {
>     var base666 = encrypts_aes(param); // 调用修复后的加密函数
>     resolve(base666);
> });

### 配置Yakit

在yakit中下载插件jsrpc、添加JSRPC接受处理

> handle=func getEnc(data){
>
> ​    parsedData = json.dumps(data);
>
> ​    rsp,rep,err = poc.Post("http://127.0.0.1:12080/go",poc.replaceBody("group=zzz&action=decrypt&param="+parsedData, false),poc.appendHeader("content-type", "application/x-www-form-urlencoded"))
>
> ​    if(err){return(err)
>
> ​    }
>
>  
>
> ​    return json.loads(rsp.GetBody())["data"]
>
> }



抓取登录的数据包，并且添加热加载逻辑

> 测试调用：{{yak(jsrpcReq|{{payload(pass_top25)}})}}
>
> yak脚本：
>
> jsrpcReq = func(origin /*string*/) {
>
> ​    // JSrpc的group
>
> ​    group = "zzz";
>
> ​    // jsrpc的action
>
> ​    action = "decrypt";
>
>  
>
> ​    if (origin[0] == "{") {
>
> ​        rsp, rep = poc.Post(
>
> ​            "http://127.0.0.1:12080/go",
>
> ​            poc.replaceBody("group=" + group + "&action=" + action + "&param=" + json.dumps(origin), false),
>
> ​            poc.appendHeader("content-type", "application/x-www-form-urlencoded")
>
> ​        )~
>
> ​        return json.loads(rsp.GetBody())["data"];
>
> ​    } else {
>
> ​        rsp, rep = poc.Post(
>
> ​            "http://127.0.0.1:12080/go",
>
> ​            poc.replaceBody("group=" + group + "&action=" + action + "&param=" + codec.EncodeUrl(origin), false),
>
> ​            poc.appendHeader("content-type", "application/x-www-form-urlencoded")
>
> ​        )~
>
> ​        return json.loads(rsp.GetBody())["data"];
>
> ​    }
>
> }

> • 脚本流程：
>
> 1. Yakit 从 `pass_top25` 字典中取出第一个密码（如 `123456`）。
> 2. 调用 `jsrpcReq` 函数，对密码进行编码（URL 编码或 JSON 处理）。
> 3. 向本地 JsRpc 服务发送请求，触发客户端的 `decrypt` 函数进行加密。
> 4. 将加密结果替换到请求中，生成最终发送的数据包。
> 5. 自动迭代 `pass_top25` 中的 25 个密码，重复步骤 1-4，完成批量加密处理
>
> - poc.GetAllHTTPPacketPostParams 从传入的req数据包中获取所有Post参数
>
> • jsrpcReq 将 encryptedData 的值发送到jsRpc的API中，返回值是加密后的参数值
>
> • poc.ReplaceHTTPPacketPostParam 替换req中Post参数名为encryptedData的参数值，然后将修改后的数据包返回

抓取登录的数据包

![image-20250803182709010](./images/Yakit%E7%83%AD%E5%8A%A0%E8%BD%BD&%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95&%E6%A8%A1%E7%89%88%E6%8F%92%E4%BB%B6%E8%AF%AD%E6%B3%95&JSRpc%E8%BF%9B%E9%98%B6%E8%B0%83%E7%94%A8&%E6%8E%A5%E5%8F%A3%E8%81%94%E5%8A%A8/image-20250803182709010.png)

配置好后就可以爆破了，热加载会进行自动处理

`encryptedData={"username":"admin","password":"{{payload(pass_top25)}}"}`

将发送的数据处理为下面加密后的数据。热加载采用了魔术方法，详细参考yakit官网

encryptedData=nArXfVdnoe67UzojAPP2X%2B6qSiznLMBAI3a5Bi%2BzlNy2Cq4NzXvYfJEx5zzudTHN

补充异步：

https://mp.weixin.qq.com/s/amnuUWLBRg3Cqb70PLgYMQ

https://mp.weixin.qq.com/s/udTWXcmXhr3w34Xp-LEaTg

https://mp.weixin.qq.com/s/HlVc0DGjSSSdbw7z6Ae09g





















































