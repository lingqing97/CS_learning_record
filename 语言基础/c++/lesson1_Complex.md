### Complex类代码解析(一)
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
//成员函数重载
inline complex& complex::operator +=(const complex& r){
    return __doapl(this,r);
}
//友元函数定义
inline complex& __doapl(complex* ths,const complex& r){
    //自由取得friend的private成员
    ths->re+=r.re;
    ths->im+=r.im;
    return *ths;
}
//非成员函数重载
//下面这些函数绝不可return by reference
//因为返回的值都是在函数内临时创建的
inline complex operator+ (const complex&x,const complex& y){
    return complex(real(x)+real(h),imge(x)+imge(y));
}
inline complex operator+ (const complex& x,double y){
    return complex(real(x)+y,imge(x));
}
inline complex operator+ (double x,const complex& y){
    return complex(x+real(y),imge(y));
}

//用法cout<<+x;
inline complex operator+(const complex& x){
    return x;
}
//用法cout<<-x;
inline complex operator-(const complex& x){
    return complex(-real(x),-image(x));
}

//重载等于运算符
inline bool operator ++(const complex& x,const complex& y){
    retur real(x)==real(y)&&imge(x)==imge(y);
}
//...
//全局函数
inline double imag(const complex& x){
    return x.imge();
}
inline double real(const complex& x){
    return x.real();
}
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

* 在含有`return`语句的循环后面应该也有一条`return`语句，如果没有的话该程序就是错误的。很多编译器都无法发现此类错误。
* 若返回引用，则引用所引的对象应该是在函数之前已经存在的

##### 扩展:引用返回左值

```c++
char &get_val(string& str,string::size_type ix){
    return str[ix];
}
int main(){
    string s("a value");
    cout<<s<<endl;
    get_val(s,0)='A';   //将s[0]的值改为A
    cout<<s<<endl;      //输出A value
    return 0;
}
```
如果返回类型是常量引用，我们不能给调用的结果赋值。

#### 知识点8:友元friend

* 类可以允许其他类或者函数访问它的非公有成员，方法是令其他类或者函数成为它的**友元(friend)**.
* 友元声明只能出现在类定义的内部，但是在类内出现的具体位置不限。友元不是类的成员也**不受它所在区域控制级别的约束**。一般来说，最好在类定义开始或者结束前的位置集中声明友元。
* 为了使友元对类的用户可见，我们通常把友元的声明(除了类内部的友元声明之外)与类本身放置在同一个头文件中(放置在类的外部)。
* 友元的利:可以访问私有成员；友元的弊:破坏了封装性.

* **相同class的各个objects互为friends.**

```c++
//相同class的各个objects互为friends
class complex{
    public:
        complex(double r=0,double i=0):re(r),im(i){}
        int func(const complex& param){ return param.re+param.im; }
    private:
        double re,im;
}

int main(){
    complex c1(2,1);
    complex c2;

    c2.func(c1);    //c2可以直接访问c1的私有变量
    return 0;
}
```

#### 知识点9:操作符重载

* 如果一个重载运算符函数是成员函数则它的第一个（左侧）运算对象绑定到隐式的this指针上。
* 对于一个运算符函数来说，它或者是类的成员，或者至少含有一个类类型的参数。

##### 例子:重载输入运算符`>>`和输出运算符`>>`

* 输入输出运算符必须是非成员函数

```c++
//重载输入运算符>>
//返回引用
istream &operator>>(istream &is,Sales_data &item){
    double prices;  //不需要初始化
    is >> item.bookNo >> item.units_sold >>price;
    if(is) //检测输入是否成功
        item.revenue=item.units_sold*price;
    else
        item=Sales_data(); //输入失败:对象被赋予默认的状态
    return is;
}
```

```c++
//重载输出运算符<<
//返回引用
ostream &operator<<(ostream &os,const Sales_data &item){
    os<<item.isbn()<<" "<<item.units_sold<<" "<<item.revenus<<" "<<item.avg_price();
    return os;
}
```













