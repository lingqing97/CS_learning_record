### Chapter 5

#### 条款26：尽量可能延后变量定义式的出现时间

* 尽量延后变量的定义，直到非得使用该变量的前一刻为止，甚至应该尝试延后这份定义知道能够给它初值实参为止
  * 更深一层说，以“具明显意义之初值”将变量初始化，还可以附带说明变量的目的

```cpp
//原函数
std::string encryptPassword(const std::string& password){
    using namespace std;
    string encrypted;
    if(password.length()<MinimumPasswordLength){
        throw logic_error("Password is too shor");
    }
    ...     //必要动作，能将一个加密后的密码置入变量encrypted内
    return encrypted;
}

//修改后的函数:延后encrypted的定义，直到真正需要它
std::string encryptPassword(const std::string& password){
    using namespace std;
    if(password.length()<MinimumPasswordLength){
        throw logic_error("Password is too shor");
    }
    string encrypted;
    ...
    return encrypted;
}
```

#### 条款27:尽量少做转型动作

* C++提供四种新式转型:
    1. `const_cast<T>(expression)`:通常被用来将对象的常量性转移
    2. `dynamic_cast<T>(expression)`:主要用来执行“安全向下转型”,也就是来决定某对象是否归属继承体系中的某个类型
    3. `reinterpret_cast<T>(expression)`:执行低级转型，实际动作（及结果）可能取决于编译器，这也就表示它不可移植
    4. `static_cast<T>(expression)`:用来强迫隐式转换,但它无法将`const`转为`non-const`(这个只有`const_cast`才办得到)
* 任何一个类型转换（不论是通过转型操作而进行的显式转换，或通过编译器完成的隐式转换）往往真的令编译器编译出运行期间执行的码，也就是说类型转换也是需要代价的
* 宁可使用`C++-style`(新式)转型，不要使用旧式转型

#### 条款28:避免返回`handles`指向对象内部成分

* `Reference`、指针和迭代器统统都是所谓的`handles`(号码牌，用来取得某个对象)，而返回一个“代表对象内部数据”的`handle`，它可能导致"虽然调用`const`成员函数却造成对象状态被更改"
* 避免返回`handles`(包括references、指针、迭代器)指向对象内部。遵守这个条款可增加封装性，帮助`const`成员函数的行为像个`const`,并将发生"虚吊号码牌"(dangling handles)的可能性降至最低

```cpp
//例子一：调用const成员函数却造成对象状态被更改
class Point{
    public:
        Point(int x,int y);
        ...
        void setX(int newVal);
        void setY(int newVal);
};
struct RectData{
    Point ulhc;     //左上角的点:ulhc=upper left-hand corner
    Point lrhc;     //右下角的点:lrhc=lower right-hand corner
};

class Rectangle{
    public:
        ...
        //返回引用可能导致private数据被修改
        Point& upperLeft() const { return pData->ulhc;}
        Point& lowerRight() const { return pData->lrhc;}
        ...
    private:
        std::shared_ptr<RectData> pData;  
};


//例子二：导致虚吊号码牌
class GPUObject { ... };
const Rectangle
    boundingBox(const GUIObect& obj);   //以by value 方式返回一个矩形

GUIObject* gpo;     //让pgo指向某个GUIObject
...
//boudningBox临时返回的Rectangel在该语句结束后被销毁，导致指针pUpperLeft悬空
const Point* pUpperLeft=
    &(boundingBox(*pgo).upperLeft());   //取得一个指针指向外框左上点
```

#### 条例29:为"异常安全"而努力是值得的

* 异常安全函数(`Exception-safe function`)提供以下三个保证之一:
  * 基本承诺:如果异常被抛出，程序内的任何事物仍然保持在有效状态下，但程序的现实状态不可预料.
  * 强烈保证:如果异常被抛出，程序状态不改变，如果函数失败，程序会恢复到“调用函数之前”的状态.
  * 不抛掷(nothrow)保证:承诺绝不抛出异常。作用于内置类型（例如ints,指针等等）身上的所有操作都提供`nothrow`保证

* `copy and swap`是一个一般化的异常安全设计策略:为打算修改的对象(原件)做出一份副本，然后在那副本身上做一切必要修改。若抛出异常，原对象仍保持未改变状态。待所有改变都成功后，再将修改过的那个副本和原对象在一个不抛出异常的操作中置换(swap)
* 函数提供的“异常安全保证”通常最高只等于其所调用之各个函数的“异常安全保证”中的最弱者

#### 条例30：透彻了解`inline`的里里外外

* `inline`函数背后的整体观念是，将“对此函数的每一个调用”都以函数本体替换之
* `friend`函数也可被定义于`class`内，如果真是那样，它们也是被隐喻声明为`inline`
* 一个表面上看似`inline`的函数是否真是`inline`，取决于键置环境，主要取决于编译器

#### 条例31：将文件间的编译依存关系降至最低

* 一个`class`内的指针成员指向其实现类，这般设计常被称为`pimpl`(是`pointer to implementation`的缩写)
* 支持“编译依存性最小化”的一般构想是：相依于声明式，不要相依于定义式。基于此构想的两个手段是`Handle classes`和`Interface classes`(见下例)
* `Handle classes`和`Interface classes`解除了接口和实现之间的耦合关系

```cpp
//例子一:handle classes

//Person.h
#include<string>
#include<memory>

class PersonImpl;   //Person实现类的前置声明
class Date;     //Person接口用到的classes的前置声明
class Address;

class Person{
    public:
        Person(const std::stirng &name,const Date& birthday,const Address &addr);
        std::string name() const;
        std::string birthday() const;
        std::string address() const;
        ...
    private:
        std::shared_ptr<PersonImpl> pImpl;  //指针，指向实现物
};

//Person.cpp
#include "Person.h"
#include "PersonImpl.h"     //PersonImpl有着和Person完全相同的成员函数两者接口完全相同

Person::Person(const std::string &name,const Date& birthday,const Address& addr):pImpl(new PersonImpl(name,birthday,addr))
{}

std::string Person::name() const{
    return pImpl->name();
}


//例子二:interface class
//令Person成为一种特殊的abstract base class(抽象类)，称为interface class
class RealPreson;
class Person{
    public:
        virtual ~Person();
        virtual std::string name() const=0;
        virtual std::string birthday() const=0;
        virtual std::string address() const=0;
        ...
        //定义factory(工厂)函数
        static std::shared_ptr<Person>
            create(const std::string& name,
                    const Date& birthday,
                    const Address& addr){
            return std::shared_ptr<Person>(new RealPerson(name,birthday,addr));

        }
};
class RealPerson:public Person{
    public:
        RealPerson(const std::string &name,const Date& birthday,const Address &addr):
            theName(name),theBirthDate(birthday),theAddress(addr)
            {}
        ~RealPerson() override {}
        std::string name() const override;
        std::string birthday() const override;
        std::string address() const override;
    private:
        std::string theName;
        Date theBirthDate;
        Address theAddress;
};
```

