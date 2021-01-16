### Chapter3

#### 条款13：以对象管理资源

* `RAII`守则：资源在构造期间获得，在析构期间释放
* 为防止资源泄露，使用`RAII`对象，它们在构造函数中获得资源并在析构函数中释放资源
* 两个常被使用的`RAII classes`分别是`shared_ptr`和`auto_ptr`。前者通常是较佳选择，因为其`copy`行为比较直观。若选择`auto_ptr`，复制动作会使它（被复制物）指向`null`
* `auto_ptr`和`tr1::shared_ptr`两者都在其析构函数内做`delete`而不是`delete []`动作(若需执行`delete []`需特别说明).同时`tr1::shared_ptr`的缺省行为是"当引用次数未0时删除其所指物"(解决办法是自定义一个删除器)

```cpp
//c++11:将shared_ptr用于数组，必须提供一个自定删除器
shared_ptr<int> sp(new int[10],[](int *p){ delete p;});
//将unique_ptr用于数组，不必提供一个自定义删除器
unique_ptr<int[]> up(new int[10]);
up.release();   //自动用delete[]销毁其指针


//自定义删除器
struct destination;     //表示我们正在连接什么
struct connection;      //使用连接所需的信息
connection connect(destination*);   //打开连接
void disconnect(connection);    //关闭给定的连接

void f(destination &d){
    connection c=connect(&d);
    shared_ptr<connection> p(&c,end_connection);
    //使用连接
    //当f退出时，connection会被正确关闭
}
```


#### 条款14：在资源管理类中小心`copying`行为

* 复制`RAII`对象必须一并复制它所管理的资源，所以资源的`copying`行为决定`RAII`对象的`copying`行为
* 普通而常见的`RAII class copying`行为是：抑制`copying`(比如`unqiue_ptr`)、施行引用计数法(`shared_ptr`)


#### 条款15：在资源管理类中提供对原始资源的访问

* `APIs`往往要求访问原始资源，所以每一个`RAII class`应该提供一个"取得其所管理之资源"的办法
* 对原始资源的访问可能经由显式转换或隐式转换。一般而言显式转换比较安全，但隐式转换对客户比较方便（显式转换和隐式转换见下例）

```cpp
class Font{
    public:
        ...
        //显式转换，定义get()函数
        FontHandle get() const { return f; }
        ...
};

class Font{
    public:
        ...
        operator FontHandle() const    //隐式转换函数
        {
            return f;
        }
        ...
};
```

#### 条款16：成对使用`new`和`delete`时要采用相同形式

* 使用`new`时有两件事会发生：
    1. 内存被分配出来(通过名为`operator new`的函数)
    2. 针对此内存会有一个（或更多）构造函数被调用
* 使用`delete`时也有两件事会发生：
    1. 针对此内存会有一个（或更多）析构函数被调用
    2. 内存被释放（通过名为`operator delete`的函数）
* 数组所用的内存通常还包括“数组大小”的记录，以便`delete`知道需要调用多少次析构函数
* 如果在`new`表达式中使用`[]`,必须在相应的`delete`表达式中也使用`[]`。如果在`new`表达式中不使用`[]`,一定不要在相应的`delete`表达式中使用`[]`


#### 条款17：以独立语句将`newed`对象置入智能指针

* 以独立语句将`newed`对象存储于智能指针内。如果不这样做，一旦异常被抛出，有可能导致难以察觉的资源泄露.（见下例）

```cpp
//以下为《Effective C++》例子，C++11现已经支持shared_ptr
//不是独立语句
processWidget(std::tr1::shared_ptr<Widget>(new Widget),priority());
//上述语句，编译器要做三件事情:
//1.调用priority
//2.执行new Widget
//3.调用tr1::shared_ptr构造函数
//由于这三者执行的顺序C++无法确定，所以若先执行new Widget,之后执行priority出现异常，则可能导致资源泄露

//使用独立语句
std::tr1::shared_ptr<Widget> pw(new Widget);
processWidget(pw,priority());
```
