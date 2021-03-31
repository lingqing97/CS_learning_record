## Day-4

### 问题

> 请说出const尽可能多的作用

### 参考答案

参考:[C++ const关键字总结](https://blog.csdn.net/marsjhao/article/details/81543158)

`const`在`C++`中的用法可以分为以下几类:

* 常变量: `const + 类型 + 变量名`  / `类型 + const + 变量名`
* 常引用: `const + 类型 + &引用名` / `类型 + const + &引用名`
* 常指针: `类型 + *const + 指针名`
* 指向常量的指针: `const + 类型 + *指针名`
* 常数组: `const + 类型 + 数组名[大小]` / `类型 + const + 数组名[大小]`
* 常对象: `const + 类名 + 对象名` / `类名 + const + 对象名`
* 常数据成员: `const + 类型 + 数据成员名`
* 常成员函数: `类型 + 类名:fun(形参) + const`

#### 常变量


