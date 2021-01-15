### Chapter2

#### 条款05:了解`C++`默默编写并调用哪些函数

* 编译器可以暗自为`class`创建`default`构造函数,`copy`构造函数,`copy assignment`操作符，以及构造函数
* 编译器产出的析构函数是个`non-virtual`，除非这个`class`的`base class`自身声明有`virtual`析构函数
* `copy assignmet`函数被编译器默认构造出来需要满足以下条件
    1. 不包含`reference`成员和`const`成员
    2. 某个`base classes`将`copy assignment`操作符声明为`private`,编译器将拒绝为其`derived classes`生成一个`copy assignment`操作符

#### 条款06:若不想使用编译器自动生成的函数，就该明确拒绝

* 为驳回编译器自动(暗自)提供的机能，可将相应的成员函数声明为`private`并且不予实现。(见下例)

```cpp
//例子：阻止类被拷贝

//阻止编译器自动生成函数的方法一

//将成员函数声明为`private`
class HomeForSale{
    public:
        ...
    private:
        ...
        HomeForSale(const HomeForSale&);    //只有声明不实现
        HomeForSale& operator=(const HomeForSale&);
};


//方法二
//可能有很多类需要阻止，所以可以声明一个统一的类
class Uncopyable{
    protected:
        Uncopyable() {}
        ~Uncopyable() {}
    private:
        Uncopyable(const Uncopyable&);
        Uncopyable& operator=(const Uncopyable&);
};

//class不在声明copy构造函数和copy assign操作符
class HomeForSale:private Uncopyable{
    ...
};
```

#### 条款07:为多态基类声明`virtual`析构函数

* 带多态性质的`base classes`应该声明一个`virtual`析构函数
* 只有当`class`内含至少一个`virtual`函数，才为它声明`virtual`析构函数
* `classes`的设计目的如果不是作为`base class`使用，或不是为了具备多态性，就不应该声明`virtual`析构函数

> 无端将所有析构函数都声明为`virtual`会造成资源的浪费

#### 条款08:别让异常逃离析构函数

* 若析构函数为正确处理异常导致异常跳出析构函数，则程序无法正常析构对象
* 析构函数绝对不要吐出异常。如果一个被析构函数调用的函数可能抛出异常，析构函数应该捕捉任何异常，然后吞下它们(不传播)或结束程序。
* 如果客户需要对某个操作函数运行期间抛出的异常做出反应，那么`class`应该提供一个普通函数(而非在析构函数中)执行该操作.(见下例)

```cpp
class DBCnn{
    public:
        ...
        //给客户提供一个自行选择的close()函数
        void close(){
            db.close();
            closed=true;
        }
        ~DBCnn(){
            if(!closed){
                try{
                    db.close();
                }
                catch(...){
                    制作运转记录，记下对close的调用失败
                    ...
                }
            }
        }
    private:
        DBConnection db;
        bool closed;
};
```

#### 条款09:绝不在构造和析构过程中调用`virtual`函数

* 在构造和析构期间不要调用`virtual`函数，因为这类调用从不下降至`derived calss`
* 在`derived class`对象的`base class`构造期间，对象的类型是`base class`而不是`derived class`,所以此时`virtual`函数会被编译器解析为`base class`

#### 条款10:令`operator=`返回一个`reference to *this`

* 令赋值(`=`,`+=`,`-=`,`*=`等)操作返回一个`reference to *this`


#### 条款11:在`operator=`中处理"自我赋值"

* 在`operator=`中需要特别注意"自我赋值",传统的做法是加上一个"证同测试"（见下例）

```cpp
class Bitmap{...};
class Widget{
    ...
    private:
        Bitmap* pb;
};
Widge& Widget::operator=(const Widget& rhs){
    //证同测试
    if(this==&rhs) return *this;

    delete pb;
    pb=new Bitmap(*rhs.pb);
    return *this;
}
```

#### 条款12:复制对象时勿忘其每一个成分

* 当编写一个`copying`函数，请确保:
    1. 复制所有`local`成员变量
    2. 调用所有`base classes`内的适当的`copying`函数
* 永远不要令`copy assignment`操作符调用`copy`构造函数，同理，不要令`copy`构造函数调用`copy assignment`操作符
* 当`copy`构造函数和`copy assignment`操作符含有相近的代码，消除重复代码的做法是，建立一个新的成员函数给两者调用。（这样的函数往往是`private`而且常被命名为`init`）
