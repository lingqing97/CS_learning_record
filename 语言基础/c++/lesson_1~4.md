### Complex类代码解析
```cpp
#ifndef __COMPLEX
#define __COMPLEX

//前置声明
class ostream;
class complex;

complex& __doapl(complex* this,const complex& r);
//类声明
class complex
{
    public:
        //构造函数
        //这里使用的初始化列表初始化成员变量
        complex(double r=0,double i=0):re(r),im(i) {}
        //运算符重载
        complex& operator +=(const complex&);
        //返回实数部分
        double real() const {return re;}
        //返回虚数部分
        double image() const {return im;}
    private:
        //定义私有变量
        double re,im;
        //定义友元函数
        friend complex& __doapl (complex*, const complex&);
};
//类定义
complex::functino ...

#endif
```

#### 知识点1:防御式声明避免头文件中的函数或类被重复调用

```cpp
#ifndef __COMPLEX__
#define __COMPLEX__
//代码段
//...
//代码段
#endif
```

#### 知识点2:inline内联函数

* 相当于把内联函数里面的内容复制到调用内联函数处
* 相比于宏，多了类型检测，真正具有函数特性
* 在类声明中定义的函数，除了虚函数的其他函数都会自动隐式地当成内联函数

* 优点:
    1. 省去了函数栈开辟等步骤，提高了程序运行速度
    2. 相比于宏可调试，会做类型检测
* 缺点:
    1. 代码膨胀，消耗更多内存空间
    2. 是否内联，程序员不可控，**内联函数只是对编译器的建议，是否对函数内联，决定权在于编译器**

#### 知识点3:访问级别

C++类中有`public`,`private`,`protected`三种访问级别(权限),访问规则总结如下:


| 访问权限 | public | protected | private |
|  ----  | ----  |  ----  | ----  |
| 对本类 | 可见 | 可见 | 可见 |
| 对子类 | 可见 | 可见 | 不可见 |
| 对外部(调用方) | 可见 | 不可见 | 不可见 |

##### 补充:C++中的struct和class

区别:
* 最本质的区别就是默认的访问权限:struct作为数据结构的实现体，它默认的数据访问控制是public的，而class作为对象的实现体，它默认的成员变量访问控制是private的.

#### 知识点4:构造函数

* 如果我们没有为类显式地定义构造函数，则类会通过一个**默认构造函数**初始化.(编译器创建的构造函数又被称为**合成的默认构造函数**)
* 只有当类没有声明任何构造函数时，编译器才会自动地生成默认构造函数.
* 构造函数初始化列表，其好处如下:
    1. 更高效:少了一次调用默认构造函数的过程
    2. 有些场合必须要用初始化列表:
       1. 常量成员,因为常量只能初始化不能赋值，所以必须放在初始化列表里面
       2. 引用类型,引用必须在定义的时候初始化，并且不能重新赋值，所以也要写在初始化列表里面
       3. 没有默认构造函数的类类型，因为使用初始化列表可以不必调用默认构造函数来初始化

##### 补充:单例模式

把构造函数放在private区域，使得外部无法定义类,这样的定义通常用于单例模式中.

```c++
//单例模式例子
class A{
    public:
        static A& getInstance();
        setup() {...}
    private:
        A();
        A(const A& rhs);
};

A& A::getInstance(){
    static A a;
    return a;
}

//调用
A::getInstance().setup();
```
#### 知识点5:const使用

* const修饰成员函数，说明该成员函数内不能修改成员变量
* const修饰变量，说明该变量不可以被改变
* const修饰指针
    1. 指向常量的指针(pointer to const)
    2. 自身是常量的指针(常量指针,const pointer)
* const修饰引用
    1. 指向常量的引用(reference to const)
    2. 没有const reference,因为引用本身就是const pointer

```c++
// 类
class A
{
private:
    const int a;                // 常对象成员，只能在初始化列表赋值

public:
    // 构造函数
    A() : a(0) { };
    A(int x) : a(x) { };        // 初始化列表

    // const可用于对重载函数的区分
    int getValue();             // 普通成员函数
    int getValue() const;       // 常成员函数，不得修改类中的任何数据成员的值
};

void function()
{
    // 对象
    A b;                        // 普通对象，可以调用全部成员函数、更新常成员变量
    const A a;                  // 常对象，只能调用常成员函数
    const A *p = &a;            // 指针变量，指向常对象
    const A &q = a;             // 指向常对象的引用

    // 指针
    char greeting[] = "Hello";
    char* p1 = greeting;                // 指针变量，指向字符数组变量
    const char* p2 = greeting;          // 指针变量，指向字符数组常量（const 后面是 char，说明指向的字符（char）不可改变）
    char* const p3 = greeting;          // 自身是常量的指针，指向字符数组变量（const 后面是 p3，说明 p3 指针自身不可改变）
    const char* const p4 = greeting;    // 自身是常量的指针，指向字符数组常量
}

// 函数
void function1(const int Var);           // 传递过来的参数在函数内不可变
void function2(const char* Var);         // 参数指针所指内容为常量
void function3(char* const Var);         // 参数指针为常量
void function4(const int& Var);          // 引用参数在函数内为常量

// 函数返回值
const int function5();      // 返回一个常数
const int* function6();     // 返回一个指向常量的指针变量，使用：const int *p = function6();
int* const function7();     // 返回一个指向变量的常指针，使用：int* const p = function7();
```

#### 知识点6:参数传递pass by value vs. pass by reference

* pass by value:函数对传值形参的所有操作都不会影响实参
* pass by reference:函数对引用形参的修改会影响实参，如果函数无须改变引用形参的值，最好将其声明为常量引用
* 在参数传递时，尽量使用pass by reference,理由如下:
    1. 使用引用可以避免拷贝，提高了程序效率
    2. 使用引用形参可以返回额外信息，一个函数只能返回一个值，通过引用我们可以返回多个值


#### 知识点7:返回值传递return by value vs. return by reference









