### Chapter4


#### 条款18:让接口容易被正确使用，不易被误用

* "促进正确使用"的办法包括接口的一致性，以及与内置类型的行为兼容
* "阻止误用"的办法包括建立新类型、限制类型上的操作，束缚对象值，以及消除客户的资源管理责任
* 任何接口如果要求客户必须记得做某些事情，就是有着“不正确使用”的倾向，因为客户可能会忘记做那件事

```cpp
//建立新类型的例子

//初始版
//初始版可能客户会将month赋予错误的值
class Date{
    public:
        Date(int month,int day,int year);
        ...
};

//将month建立为新类型
class MOnth{
    public:
        static Month Jan() { return Month(1); }
        static Month Feb() { return Month(2); }
        ...
        static Month Dec() { return Month(12); }
    private:
        //阻止生成新的月份
        //月份的专属数据
        explicit Month(int m);
};

Date d(Month::Mar(),Day(30),Year(1995));
```

#### 条款19:设计`class`犹如设计`type`

* `class`的设计就是`type`的设计


#### 条款20:宁以`pass-by-reference-to-const`替换`pass-by-value`

* `pass-by-value`的不好之处主要在于两点:
    1. `pass-by-value`往往需要调用`copy`构造函数，代价一般较大
    2. `pass-by-value`会导致`derived class`向`base class`传递时被`slicing`(对象切割)
* 一般而言，可以合理假设`pass-by-value`并不昂贵的唯一对象就是内置类型和STL的迭代器和函数对象。至于其他任何东西尽量以`pass-by-reference-to-const`替换`pass-by-value`

#### 条款21:必须返回对象时，别妄想返回其`reference`

* 绝不要返回`pointer`或`reference`指向一个`local stack`对象，或返回`reference`指向一个`heap-allocated`对象，或返回`pointer`或`reference`指向一个`local static`对象。（下面是一些反面例子）

```cpp
//定义一个有理数类
class Rational{
    public:
        Rational(int numerator=0,int denominator=-1);
    private:
        int n,d;    //分子(numerator)和分母(denominator)
    friend const Rational operator* (const Rational &lhs,const Rational &rhs);
};

//错误示例一：返回local stack对象
//local stack在函数返回后会被系统释放
const Rational operator*(const Rational &lhs,const Rational &rhs){
    //警告:糟糕的代码!
    Raional result(lhs.n*rhs.n,lhs.d*rhs.d);
    return result;
}

//错误示例二：返回heap allocated对象
//heap allocated对象没有被释放，造成内存泄露
const Rational operator*(const Rational &lhs,const Rational &rhs){
    //警告：糟糕的代码!
    Raional* result=new Rational(lhs.n*rhs.n,lhs.d*rhs.d);
    return *result;
}

//错误示例三:返回local static对象
//当使用(a*b)==(c*d) 时结果无论如何都是true，因为result指向同一个static对象
const Rational& operator*(const Rational &lhs,const Rational &rhs){
    //警告：烂代码!
    static Rational result;
    result=...;
    return result;
}

//正确示例：返回value
inline const Rational& operator*(const Rational &lhs,const Rational &rhs){
    return Rational(lhs.n*rhs.n,lhs.d*rhs.d);
}
```

#### 条款22:将成员变量声明为`private`

* 成员的封装性与"成员变量的内容改变时所破坏的代码数量"成反比
* 切记将成员变量声明为`private`
* `protected`并不比`public`更具封装性
* 从封装的角度，其实只有两种访问权限：`private`(提供封装)和其他(不提供封装)

#### 条款23:宁以`non-member,non-friend`替换`member`函数

* 有些时候使用`non-member,non-friend`函数比使用`member`函数要好

```cpp
class WebBrowser{
    public:
        ...
        void clearCache();
        void clearHistory();
        void removeCookie();
        ...
        //这里定义为member函数并不好
        void clearEverything();     //调用clearCache,clearHistory和removeCookies
};

//定义为non-member函数,较好在这里
void clearBrowser(WebBrowser& wb){
    wb.clearCache();
    wb.clearHistory();
    wb.removeCookies();
}
```

#### 条款24:若所有参数皆需类型转换，请为此采用`non-member`函数

* 如果需要为某个函数的所有参数（包括被this指针所指的那个隐喻参数）进行类型转换，那么这个函数必须是个`non-member`(典型的例子就是“重载具有对称性质的运算符”,比如`+`,`-`,`*`,`/`等)
* 一个“与某class相关”的函数不一定要被声明为`friend`，要看实际是否调用了`class`的`private`接口

#### 条款25:考虑写出一个不抛异常的`swap`函数

* STL内置的swap实现大体如下例所示(下例中若使用内置swap函数性能会大打折扣)
* 当使用内置的swap性能不太好的时候，可以针对class定制swap函数，定义的swap函数遵化一下步骤:
    1. 提供一个`public swap`成员函数，让它高效地置换两个对象值,**同时这个`swap`函数绝不该抛出异常**
    2. 在你的`clas`或`template`所在的命名空间内提供一个`non-member swap`，并令它调用上述`swap`函数
    3. 如果编写一个`class`(而非`class template`)，为你的`class`特化`std::swap`，并令它调用`swap`成员函数
    4.最后如果调用`swap`，请确定包含一个`using`声明式，以便让`std::swap`在你的函数内曝光可见，然后不加任何`namespace`修饰符，赤裸裸地调用`swap`

```cpp
namespace std{
    //内置swap大体实现
    template<typename T>
    void swap(T &a,T &b){
        T temp(a);
        a=b;
        b=temp;
    }
}

//自定义swap函数的典型实现
//针对Widget数据而设计的class
class WidgetImpl{
    public:
        ...
    private:
        int a,b,c;
        std::vector<double> v;
};
class Widget{
    public:
        ...
        void swap(Widget &other){
            using std::swap;
            swap(pImpl,other.pImpl);
        }
        ...
    private:
        WidgetImpl* pImpl;
};
namespace std{
    //TODO
    //?????????
    template<>
    void swap<Widget>(Widget &a,Widget &b){
        a.swap(b);
    }
}
```