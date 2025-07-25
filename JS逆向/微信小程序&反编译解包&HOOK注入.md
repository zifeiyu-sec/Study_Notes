思考：js逆向为什么会讲到小程序，不会说app
微信特定版本和小程序版本
https://github.com/tom-snow/wechat-windows-versions
https://github.com/JaveleyQAQ/WeChatOpenDevTools-Python

## 微信小程序反编译

https://github.com/biggerstar/wedecode

https://github.com/Angels-Ray/UnpackMiniApp

下载安装上面两个工具

随便选择一个小程序运行

![image-20250721233848610](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233848610.png)



运行wedecode工具

![image-20250721232838315](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721232838315.png)

选择第三个选项，

![image-20250721233001342](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233001342.png)

打开文件夹后进入上一级目录，然后点击进入applet目录。此时会有类似下面的文件

![image-20250721233130122](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233130122.png)

一串字符那个文件就是我们打开的小程序。

进去之后因为现在的大多数小程序都有加密，先使用另外一款工具进行解密

运行加密软件后如下图选择文件解密

![image-20250721233417027](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233417027.png)

加密后如下会给出一个目录文件

![image-20250721233457589](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233457589.png)

基础解密后文件所处的文件夹。

回到第一个工具。输入刚才的文件夹路径路径

![image-20250721233627912](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233627912.png)

然后就开始解密了。解密完成给出下图所示的路径

![image-20250721233733986](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233733986.png)

解密结果

![image-20250721233755385](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250721233755385.png)

成功反编译

## 调试

使用微信开发者工具对于反编译出来的项目，可能无法做到很好的调试

本人使用的微信版本是3.9.10.19，小程序可以通过进程查看，我的是8555_X64,

在调试如果遇到微信小程序版本过高，可以参考本人GitHub其他文件夹中`微信修改小程序版本`的文章

WechatOpenDevTools-Python工具可以对小程序进行很好的调试

工具链接：https://github.com/JaveleyQAQ/WeChatOpenDevTools-Python

![image-20250722194934980](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250722194934980.png)

下载工具后直接运行。就可以。然后打开微信小程序。

![image-20250722195037056](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250722195037056.png)

此时就会有上图所示的选项，点击后就可以调试了。

如图所示

![image-20250722195257148](./%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F&%E5%8F%8D%E7%BC%96%E8%AF%91%E8%A7%A3%E5%8C%85&HOOK%E6%B3%A8%E5%85%A5.assets/image-20250722195257148.png)

### 既然已经可以通过工具进行F12调试了，**为什么有时候仍然需要反编译？**

### **案例1：分析加密逻辑**

- 如果小程序使用 **自定义加密算法**（如对API请求参数签名），直接调试可能只能看到 **加密后的结果**，而无法知道 **加密过程**。
- **反编译** 可以找到加密函数（如 `md5`、`AES`），并分析其实现方式。

### **案例2：绕过授权检测**

- 某些小程序会检测 **是否在官方环境运行**（如 `wx.getSystemInfoSync()`判断是否在微信里）。
- **直接调试** 可能无法绕过，但 **反编译** 可以修改检测逻辑，使其在非官方环境运行。

### **案例3：研究闭源小程序的实现**

- 如果你想学习某个 **优秀小程序的架构**（如美团、拼多多），直接调试只能看到 **片段**，而 **反编译** 可以获取完整代码结构。



可以调试后结合反编译就可以对小程序的js进行逆向了，分析加密手法，sign签名等，和浏览器调试差不多。
