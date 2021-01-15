### Chapter1

#### 条款01：视`c++` 为一个语言联邦

* C++可以分为四个次语言:
  * C语言
  * Object-Oriented C++(C with class)
  * Template C++(范型编程)
  * STL(标准模板库)

#### 条款02：尽量以`const`,`enum`,`inline`替换`#define`

* 对于单纯常量，最好以`const`对象或者`enums`替换`#fefine`
* 对于形似函数的宏,最好改用`inline`函数替换`#define`

#### 条款03：尽量可能使用`const`

* 指向常量的指针有两种书写格式:
    1. `const typename * p`
    2. `typename const * p`
* 两个成员函数如果只是常量性不同，可以被重载
* 对于`const`,`C++`遵循`bitwise constness`
  * 漏洞：对于一个更改了“指针所指物”的成员函数虽然不能算是`const`,但如果只有指针(而非其所指物) 隶属于对象，那么称此函数为`bitwise const`不会引发编译器异议（但不适当）。
* 在`const`和`non-const`成员函数中避免重复:`non-const`函数调用`const`函数(见下面的例子)

```cpp
class TextBlock{
    public:
    ...
    const char& operator[](std::size_t position) const
    {
        ...
        return text[position];
    }
    ..
    char& operator[](std::size_t position)
    {
        return const_cast<char&>(
            static_cast<const TextBlock&>(*this)[position];
        )
    }
};
```

#### 条款04：确定对象被使用前已先被初始化

* 使用未初始化的对象可能导致程序出现未定义行为，为避免出现这种情况，需要做三件事:
    1. 手工初始化内置型`non-member`对象
    2. 使用成员初值列(`member initialization list`)对付对象的所有成分,比直接赋值效率更高
    3. 在“初始化次序不确定”(比如不同编译单元所定义的`non-local static`)氛围下加强设计(见下面的例子)

```cpp
//使用reference-return local static对象避免初始化次序不确定造成的错误

//test1.cpp
class FileSystem{
    ...
};
FileSystem tfs(){
    static FileSystem fs;
    return fs;
}

//test2.cpp
class Directory{
    ...
    std::size_t disks=tfs.numDisks();
};
Directory& tempDir(){
    static Directory td;
    return td;
}
```
