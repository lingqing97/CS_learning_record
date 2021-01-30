### chapter7 类

#### 7.1 定义抽象数据类型

* 成员函数的声明必须在类的内部，它的定义则既可以在类的内部也可以在类的外部
  * 定义在类内部的函数是隐式的`inline`函数
  * 成员函数通过一个名为`this`的额外的隐式参数来访问调用它的那个对象,默认情况下`this`的类型是`指向类类型非常量版本的常量指针`
  * `const`关键字放在成员函数的参数列表之后，此时紧跟在参数列表后面的`const`表示`this`是一个指向常量的指针，这样的成员函数称为`常量成员函数`
  * 常量对象，以及常量对象的引用或指针都只能调用常量成员函数
  * 类的处理分为两步：首先编译成员的声明，然后才轮到成员函数体，因此成员函数体可以随意使用类中的其他成员而无须在意这些成员出现的次序
* 一般来说，如果非成员函数是类接口的组成部分，则这些函数的声明应该与类在同一个头文件内
* 类通过一个或几个特殊的成员函数来控制其对象的初始化过程，这些函数叫做`构造函数`
  * `构造函数`没有返回类型
  * `构造函数`不能被声明成`const`的，当我们创建类的一个`const`对象时，直到构造函数完成初始化过程，对象才真正取得其"常量"属性，因此构造函数在`const`对象的构造过程中可以向其写值
  * 编译器创建的构造函数又称为`合成的构造函数`,编译器只有在发现类不包含任何构造函数的情况下才会替我们生成一个默认的构造函数

#### 7.2 访问控制与封装

* 在c++语言中，我么使用`访问说明符`加强类的封装性:
  * 定义在`public`说明符之后的成员在整个程序内可被访问，`public`成员定义类的接口
  * 定义在`private`说明符之后的成员可以被类的成员函数访问，但是不能被使用该类的代码访问，`private`部分封装了类的实现细节
  * 每个访问说明符指定了接下来的成员的访问级别，其有效范围直到出现下一个访问说明符或者到达类的结尾为止
* `struct`和`class`的默认访问权限不太一样:
  * 如果我们使用`struct`关键字，则定义在第一个访问说明符之前的成员是`public`的；相反，如果我们使用`class`关键字，则这些成员是`private`的
  * 当我们希望定义的类的所有成员是`public`的时，使用`struct`；反之，如果希望成员是`private`的，使用`class`
* 类可以允许其他类或者函数访问它的非公有成员，方法是令其他类或者函数成为它的`友元`,只需增加一条以`friend`关键字开始的函数声明语句即可
  * 友元不是类的成员也不受它所在区域访问控制级别的约束，一般来说，<font color=red>最好在类定义开始或结束前的位置集中声明友元</font>

#### 7.3 类的其他特性

* 除了定义数据和函数成员之外，类还可以自定义某种类型在类中的别名。
  * 由于类定义的类型名字和其他成员一样存在访问限制，可以是`public`或者`private`中的一种,类型成员通常出现在类开始的地方(见例子一)
* 一个`可变数据成员`永远不会是`const`，即使它是`const`对象的成员，因此一个`const`成员函数可以改变一个可变成员的值(见例子二)
* 一个`const`成员函数如果以引用的形式返回`*this`,那么它的返回类型将是常量引用(见例子三)
* 每个类定义了唯一的类型，对于类类型来说，只要名字不同则它们属于不同的类
  * 对于两个类来说，即使它们的成员完全相同，这两个类也是两个不同的类型
* 和函数的声明一样，我们可以提前声明类但不定义类，这种声明称为`前向声明`,在`前向声明`之后定义之前该类还是一个`不完全类型`
  * <font color=red>`不完全类型`只能在非常有限的情景下使用：可以定义指向这种类型的指针或引用，也可以声明以不完全类型作为参数或者返回类型的函数</font>
  * 因为只有当类全部完成后类才算被定义，所以一个类的成员类型不能是该类自己，一旦一个类的名字出现后，它就被认为是声明过了,因此允许类包含指向它自身类型的引用或指针(见例子四)
* 友元关系不存在传递性，每个类负责控制自己的友元类或友元函数
* 友元函数可以定义在类的内部，<font color=red>但即使友元函数定义在类的内部，我们仍然需要在类的外部进行相应的声明</font>(见例子五).
  * 友元声明的意义是使其对其它函数可见，友元未声明则其它函数无法调用它

```cpp
//例子一：定义一个类型成员
class Screen{
    public:
        typedef std::string::size_type pos;
    private:
        pos cursor=0;
        pos height=0,width=0;
        std::string contents;
};

//例子二：可变数据成员
class Screen{
    public:
        void some_member() const;
    private:
        mutable size_t access_ctr;  //定义一个可变数据成员
};

void Screen::some_member() const    //在const成员函数中可以改变可变数据成员
{
    ++access_ctr;
}

//例子三：基于const的重载
class Screen{
    public:
        Screen &display(std::ostream &os){
            do_display(os);
            return *this;
        }
        const Screen &display(std::ostream &os) const{
            do_display(os);
            return *this;
        }
    private:
        //该函数负责显示Screen的内容
        void do_display(std::ostream &os) const {
            os<<contents;
        }
};

//例子四：类的声明
class Link_screen{
    Screen window;
    Link_screen *next;
    Link_screen *prev;
};

//例子五：定义在类内部的友元函数
struct X{
    friend void f()
    {
        /* 友元函数可以定义在类的内部*/
    }
    X() { f(); }
    void g();
    void h();
};
void X::g() { return f(); }     //错误:f还没有声明
void f();                       //声明那个定义在X中的函数
void X::h() { return f(); }     //正确：现在f的声明在作用域中了
```

#### 7.4 类的作用域

* 一个类就是一个作用域，一旦遇到了类名，定义的剩余部分就在类的作用域之内了，这里的剩余部分包括参数列表和函数体
  * 当成员函数定义在类的外部时，返回类型中使用的名字都位于类的作用域之外，此时，返回类型必须指明它是哪个类的成员(见例子一)
* 类的定义分两步处理（编译器处理完类中的全部声明后才会处理成员函数的定义）:
  * 首先编译成员的声明
  * 直到类全部可见后才编译函数体
* 在类内部不能重新定义外部已定义的类型名字(见例子二)
* 成员函数中的名字查找是先在成员函数内查找，之后在类内部最后在类外部查找

```cpp
//例子一：定义在类外部的成员函数
class Window_mgr{
    public:
        //窗口中每个屏幕的编号
        using ScreenIndex=std::vector<Screen>::size_type;
        //向窗口添加一个Screen,返回它的编号
        ScreenIndex addScreen(const Screen&);
    private:
        std::vector<Screen> screens{Screen(24,80,' ')};
};
Window_mgr::ScreenIndex Windwo_mgr::addScreen(const Screen &s){
    screens.push_back(s);
    return screens.size()-1;
}

//例子二：重复定义类型名字
typedef double Money;
class Account{
    public:
        Money balamnce() { return bal; }
    private:
        typedef double Money;               //错误：不能重新定义Money
        Money bal;
        //...
};
```

#### 7.5 构造函数再探

* <font color=red>如果成员是`const`、引用，或者属于某种未提供默认构造函数的类类型，我们必须通过构造函数初始值列表为这些成员提供初值</font>
  * 在构造函数的初始值列表中，成员的初始化顺序与它们在类定义中的出现顺序一致，构造函数初始值列表中初始值的前后位置关系不会影响实际的初始化顺序
* 如果一个构造函数为所有参数都提供了默认实参，则它实际上也定义了默认构造函数（见例子一）
* c++11新标准扩展了构造函数初始值的功能，使得我们可以定义所谓的`委托构造函数`
  * 一个委托构造函数使用它所属类的其他构造函数执行它自己的初始化过程（见例子一）
* 如果构造函数只接受一个实参，则它实际上定义了转换为此类类型的隐式转换机制，有时我们把这种构造函数称作`转换构造函数`
  * <font color=red>只接受一个实参的构造函数需要判断一下是否需要抑制其隐式转换</font>，我们可以通过将构造函数声明为`explicit`加以阻止（见例子三）

```cpp
//例子一
class Sales_data{
    public:
        //定义默认构造函数
        Sales_data{std::string s=""}: bookNo(s) {}
        //定义委托构造函数
        Sales_data(std::string s):Sales_data(s,0,0){}
        Sales_data(std::string s,unsigned cnt,double rev):
            bookNo(s),units_sold(cnt),revenue(rev*cnt){}
        Sales_data(std::istream &is) { read(is,*this); }
    private:
        //...
};

//例子二：正确使用默认构造函数

Sales_data obj();           //错误：声明了一个不接受任何参数的函数并且其返回值是Sales_data
Sales_data obj2;            //正确：ojb2是一个对象而非函数

//例子三
class Sales_data{
    public:
        Sales_data()=default;
        Sales_data(const std::string &s,unsigned n,double p):
            bookNo(s),units_sold(n),revenue(p*n) { }
        //使用explicit阻止隐式转换
        explicit Sales_data(const std::string &s):bookNo(s) { }
        explicit Sales_data(std::istream&);
    private:
        //...
};

//explicit关键字只需要在类内的构造函数之前声明，在类外不需要再声明了
Sales_data::Sales_data(std::istream& is){
    read(is,*this);
}
```

#### 7.6 类的静态成员

* 静态成员可以是`public`的或`private`的，静态数据成员的类型可以是常量、引用、指针、类类型等
* 静态成员函数也不与任何对象绑定在一起，它们不包含`this`指针
  * 静态成员函数不能声明成`const`的，而且我们也不能在`static`函数体内使用`this`指针
  * 类的成员函数不同通过作用域运算符就能直接使用静态成员
  * 当在类的外部定义静态成员时，不能重复`static`关键字，该关键字只出现在类内部的声明语句
* 一般来说，由于静态数据成员不属于类的任何一个对象，所以我们不能在类的内部初始化静态成员，相反，<font color=red>必须在类的外部定义和初始化每个静态成员</font>
  * 我们可以为静态成员提供`const`整数类型的类内初始值，不过要求静态成员必须是字面值常量类型的`constexpr`(见例子一)

```cpp
//例子一：静态成员的类内初始化
class Account{
    public:
        static double rate() { return interestRate; }
        static void rate(double);
    private:
        static constexpr int period=30;         //period是常量表达式
        double daily_tbl[period];
};

constexpr int Account::period;                  //初始值在类的定义内提供

```


