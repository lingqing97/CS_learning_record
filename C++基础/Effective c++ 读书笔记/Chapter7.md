### Chapter7

#### 条款41：了解隐式接口和编译器多态

* `classes`和`templat`都支持接口(`interfaces`)和多态(`polymorphism`)
* 对`classes`而言接口是显式的，以函数签名为中心。多态则是通过`virtuzl`函数发生于运行期

#### 条款42：了解`typename`的双重意义

* 声明`template`参数时，前缀关键字`class`和`typename`可互换
* 请使用关键字`typename`标识嵌套从属类型名称；但不得在`base class lists`(基类列)或`member initialization list`(成员初值列)内以它作为`base class`修饰符（见下面的例子）

```cpp
//错误示例:
template<typename C>
void print2nd(const C& container){
    //报错：因为编译器不知道这是一个类型
    //如果c有个static成员变量碰巧被命名为const_iterator这样就得到的就不是一个类型
    C::const_iterator* x;
}

//正确示例:
template<typename C>
void print2nd(const C& container){
    //使用关键字typename告诉编译器这里的嵌套从属类型是个类型
    typename C::const_iterator* x;
}

//typedef的例子
template<typename IterT>
void workWithIterator(IterT iter){
    //这里将typename std::iterator_traits<IterT>::value_type看成一个整体类型比较好理解
    typedef typename std::iterator_traits<IterT>::value_type value_type;
}

//typename不得在基类列或成员初值列中修饰
template<typename T>
//这里基类列中不需要使用typename
class Derived:public Base<T>::Nested{
    public:
        //这里成员初值列中不需要使用typename
        explicit Derived(int x):Base<T>::Nested(x){
            typename Base<T>::Nested temp;
        }
};
```

#### 条款43：学习处理模块化基类内的名称

* 当我们从`Object Oriented C++`跨进`Template C++`继承就不像以前那样了(见下面的例子一)
* 在`derived class template`中可以通过三种方式告知编译器接口存在(若接口确实不存在还是会报错):
    1. 通过`this->`(见例子二)
    2. 通过`using`声明(见例子三)
    3. 通过`base class`资格修饰符(见例子四)

```cpp
//例子一：Template C++继承的异样

class CompanyA{
    public:
        ...
        void sendCleartext(const std::string& msg);
        void sendEncryped(const std::string& msg);
        ...
};

class CompanyB{
    public:
        ...
        void sendCleartext(const std::string& msg);     //发送未加密文本
        void sendEncryped(const std::string& msg);      //发送加密文本
        ...
};
...

class MsgInfo {...};    //针对其他公司设计的classes

template<typename Company>
class MsgSender{
    public:
        ...     //构造函数，析构函数
        void sendClear(const MsgInfo& info){
            std::string msg;
            Company c;
            c.sendCleartext(msg);
        }
        void sendSecret(const MsgInfo& info){
            ...
        }
};

template<typename Company>
class LoggingMsgSender:public MsgSender<Company>{
    public:
        ...
        void sendClearMsg(const MsgInfo& info){
            将“传送前”的信息写至log;
            //意图调用MsgSender<Company>::sendClear(const MsgInfo& info)
            //报错：在一个全特化的MsgSender中可能没有sendClear函数，所以编译器不允许这种写法
            sendClear(info);
            将“传送后”的信息写至log;
        }
};

class CompanyZ{
    public:
        ...
        void sendEncrypted(const std::string& msg);
};

//一个全特化的MsgSender
//MsgSender:它和一般template相同，区别只在于它删除了sendClear
template<>
class MsgSender<CompanyZ>{
    public:
        ...
        void sendSecret(const MsgInfo& info)
        { ... }
}

//例子二：使用this->告知编译器接口存在
template<typename Company>
class LoggingMsgSender:public MsgSender<Company>{
    public:
        ...
        void sendClearMsg(const MsgInfo& info){
            将“传送前”的信息写至log;
            //方式一
            this->sendClear(info);
            将“传送后”的信息写至log;
        }
};

//例子三：使用using声明告知编译器接口存在
template<typename Company>
class LoggingMsgSender:public MsgSender<Company>{
    public:
        //方式二
        using MsgSender<Company>::sendClear;    //告知编译器，请它假设sendClear位于base class内
        ...
        void sendClearMsg(const MsgInfo& info){
            将“传送前”的信息写至log;
            sendClear(info);
            将“传送后”的信息写至log;
        }
};

//例子四：使用base class资格声明告知编译器接口存在
template<typename Company>
class LoggingMsgSender:public MsgSender<Company>{
    public:
        ...
        void sendClearMsg(const MsgInfo& info){
            将“传送后”的信息写至log;
            //方式三
            MsgSender<Company>::sendClear(info);
            将“传送后”的信息写至log;
        }
};
```

#### 条款44：将与参数无关的代码抽离`templates`

* 与普通的编程一样，在使用`templates`进行编程时，我们也需要把共同的部分提取出来，避免代码的重复编写

```cpp
//例子：求任意大小矩阵的逆
template<typename T>
class SquareMatrixBase{                         //与尺寸无关的base class
    protected:
        ...
        void invert(std::size_t matrixSize);    //以给定的尺寸求逆矩阵
        ...
};

template<typename T,std::size_t n>
class SquareMatrix:private SquareMatrixBase<T>{ //这里SquareMatrix与SquareMatrixBase并不是is-a的关系，所以使用private继承
    private:
        using SquareMatrixBase<T>::invert;      //避免遮掩base版的invert
    public:
        ...
        void invert() { this->invert(n); }      //将公共代码放在SquareMatrixBase中
};
```

#### 条款45：运用成员函数模板接受所有兼容类型

* 请使用`member function templates`(成员函数模板)生成“可接受所有兼容类型”的函数(即使用`member function templates`函数泛化成员函数)(见例子一)
* 如果你声明`member templates`用于"泛化copy构造"或“泛化assignment操作”，你还是需要声明正常的copy构造函数和`copy assignment`操作符(见例子)

```cpp
//例子一：智能指针中的泛化情况
template<typename T>
class SmartPtr{
    public:
        explicit SamrtPtr(T* realPtr);
        ...
};

//将SmartPtr<Middle>转换为SmartPtr<Top>
SmartPtr<Top> pt1=SmartPtr<Middle>(new Middle);
//将SmartPtr<Bottom>转换为SmartPtr<Top>
SmartPtr<Top> pt1=SmartPtr<Bottom>(new Middle);
//将SmartPtr<Top>转换为SmartPtr<const Top>
SmartPtr<const Top> pt1=pt1;


//为了使得上述转换合法，需要为SmartPtr定义泛化copy构造函数
template<typename T>
class SmartPtr{
    public:
        template<typename U>
        SmartPtr(const SmartPtr<U>& other);     //定义一个泛化的copy构造函数
};

//例子二
template<typename T>
class shared_ptr{
    public:
        shared_ptr(shared_ptr const& r);    //copy构造函数
        template<class Y>
            shared_ptr(shared_ptr<Y> const& r);

        shared_ptr& operator=(shared_ptr const& r);     //copy assignment
        template<class Y>
            shared_ptr& operator=(shared_ptr<Y> const& r);
};
```

#### 条款46：需要类型转换时请为模板定义非成员函数

* 在`template`实参推导过程中从不将隐式转换函数纳入考虑。绝不！(见例子一)
* 要使得`template`中支持隐式转换，可以将涉及隐式转换的函数声明为`friend`(见例子)

```cpp
//例子一
template<typename T>
class Rational{
    public:
        Rational(const T& numerator=0,
                const T& denominator=1);
        const T numerator() const;
        const T denominator() const;
        ...
};
template<typename T>
const Ration<T> operator*(const Rational<T>& lhs,const Rational<T>& rhs)
{ ... }

Rational<int> oneHalf(1,2)
Rational<int> result =oneHalf *2;   //这里不能通过编译，会报错，因为在template中不能隐式转换

//正确例子
template<typename T>
class Rational{
    friend const Rational operator*(const Rational& lhs,const Rational& rhs);
    public:
        ...
};
template<typename T>
const Rational<T> operator*(const Rational& lhs,const Rational& rhs){
    ...
}

Rational<int> oneHalf(1,2)
//这里对operator*的混合式调用可以通过编译了
//因为当对象oneHale被声明为一个Rational<int>,class Rational<int>于是被具现化出来，
//而作为过程的一部分，friend函数operator*(接受Rational<int>参数)也就被自动声明出来
//而后者作为一个函数而非函数模板，因此编译器可在调用它时使用隐式转换函数，而这便是混合式调用之所以成功的原因
Rational<int> result =oneHalf *2;

//另一种实现
template<typename T>
class Rational{
    //这里的friend将是inline的!!!
    friend const Rational operator*(const Rational& lhs,
                                    const Rational& rhs)
    {
        return Rational(lhs.numerator()*rhs.numerator(),lhs.denominator()*rhs.denominator());
    }
    public:
        ...
};
```

#### 条款47：请使用`traits classes`表现类型信息


#### 条款48：认识`template`元编程

* `Template metaprogramming`(TMP,模板元编程)可将工作由运行期移往编译器，因而得以实现早期错误侦察和更高的执行效率
