### chapter13 拷贝控制

#### 13.1 拷贝、赋值与销毁

* 一个类定义了五种特殊的成员函数来控制类的对象拷贝、移动、赋值和销毁时做什么
  * `拷贝构造函数`
  * `拷贝赋值运算符`
  * `移动构造函数`
  * `移动赋值运算符`
  * `析构函数`
* 如果一个构造函数的第一个参数是自身类类型的引用，且任何额外参数都有默认值，则此构造函数是拷贝构造函数
  * 如果我们没有为一个类定义拷贝构造函数，编译器会为我们定义一个
  * 与合成默认构造函数不同，即使我们定义了其他构造函数，编译器也会为我们合成一个拷贝构造函数
* 隐式销毁一个内置指针类型的成员不会`delete`它所指向的对象，这经常造成内存泄露
  * 当指向一个对象的引用或指针离开作用域时，析构函数不会执行
* 当定义一个类时，我们显式地或隐式地指定了此类型的对象在拷贝、赋值和销毁时做什么。一个类通过定义三种特殊的成员函数来控制这些操作：`拷贝构造函数`、`拷贝赋值运算符`和`析构函数`
  * <font color=red>需要析构含的类也需要拷贝和赋值操作</font>
  * <font color=red>需要拷贝操作的类也需要赋值操作，反之亦然</font>
* 在新标准下，我们可以通过将拷贝构造函数和拷贝赋值运算符定义为`删除的函数`来阻止拷贝，在函数的参数列表后面加上`=delete`来指出我们希望将它定义为删除的（见例子一）
  * 与`=default`的不同之处是，我们可以对任何函数指定`=delete`(我们只能对编译器可以合成的默认构造函数和拷贝控制成员使用`=default`)
* 在某些情况下，合成的拷贝控制成员可能是删除的(<font color>本质上，下面规则的含义是，如果一个类有数据成员不能默认构造、拷贝、复制或销毁，则对应的成员函数将被定义为删除的</font>)：
  * 如果类的某个成员的析构函数是删除的或不可访问的（例如，是`private`的）,则类的合成析构函数被定义为删除的
  * 如果类的某个成员的拷贝构造是删除的或不可访问的（例如，是`private`的）,则类的合成拷贝构造函数被定义为删除的
  * 如果类的某个成员的拷贝赋值运算符是删除的或不可访问的（例如，是`private`的）,则类的合成拷贝赋值运算符被定义为删除的
  * 如果类的某个成员的析构函数是删除的或不可访问的，或是类有一个引用成员，它没有类内初始化器，或是类有一个`const`成员，它没有类内初始化器且类型未显示定义默认构造函数，则该类的默认构造函数被定义为删除的

```cpp
//例子一：定义删除的函数
struct NoCopy{
    NoCopy() = default;             //使用合成的默认构造函数
    NoCopy(const NoCopy&) = delete; //阻止拷贝
    NoCopy& operator=(const NoCopy&) = delete;      //阻止赋值
    ~NoCopy() = default;            //使用合成的析构函数
};
```

> 由于拷贝控制操作是由三个特殊的成员函数来完成的，所以我们称此为“C++三法则”。在较新的 C++11 标准中，为了支持移动语义，又增加了移动构造函数和移动赋值运算符，这样共有五个特殊的成员函数,所以又称为“C++五法则”。也就是说，“三法则”是针对较旧的 C++89 标准说的，“五法则”是针对较新的 C++11 标准说的。为了统一称呼，后来人们把它叫做“C++ 三/五法则”。(参考:[C++ 三/五法则- 阿玛尼迪迪- 博客园](https://www.cnblogs.com/codingmengmeng/p/9110608.html))

#### 13.2 拷贝控制和资源管理

* 类的拷贝语义，一般来说，有两种选择，可以定义拷贝操作，使得类的行为看起来像一个值或者像一个指针:
  * （*重要）类的行为像一个值，意味着它应该也有自己的状态。当我们拷贝一个像值的对象时，**副本和原对象是完全独立的**。改变副本不会对原对象有任何影响，反之亦然（类似于定义了"深拷贝"）（见例子一）
  * （*重要）**行为像指针的类则共享状态**。当我们拷贝一个这种类的对象时，**副本和原对象使用相同的底层数据**。该副本也会改变原对象，反之亦然（类似于定义了"浅拷贝"）（见例子二）

```cpp
//例子一：行为像值的类
class HasPtr{
    public:
        HasPtr(const std::string &s=std::string()):ps(new std::string(s)),i(0) { }
        //对ps指向的string,每个HasPtr对象都有自己的拷贝
        HasPtr(const HasPtr &p):ps(new std::string(*ps.ps)),i(p.i){ }
        HasPtr& operator=(const HasPtr &);
        ~HasPtr();
    private:
        std::string* ps;
        int i;
};
HasPtr& HasPtr::operator=(const HasPtr& rhs){
    //先拷贝右侧运算对象，使得可以处理自赋值的情况
    auto newp=new string(*rhs.ps);
    delete ps;
    ps=newp;
    i=rhs.i;
    return *this;
}

//例子二：行为像指针的类
class HasPtr{
    public:
        //构造函数分配新的string和新的计数器，将计数器置为1
        HasPtr(const std::string &s=std::string()):ps(new std::string(s)),i(0) ,use(new std::size_t(1)){}
        //拷贝构造函数拷贝所有三个数据成员，并递增计数器
        HasPtr(const HasPtr &p):
            ps(p.ps),i(p.i),use(p.use) { ++*p.use; }
        HasPtr& operator=(const HasPtr &);
        ~HasPtr();
    private:
        std::string* ps;
        int i;
        std::size_t *use;           //用来记录有多少个独享共享*ps对象
};
HasPtr& HasPtr::operator=(const HasPtr &rhs){
    ++*rhs.use;                     //递增右侧运算对象的引用计数
    if(--*use==0){                  //递减本对象的引用计数
        delete ps;                  //如果没有其他用户，释放本对象分配的成员
        delete use;
    }
    ps=rhs.ps;                      //将数据从rhs拷贝到本对象
    i=rhs.i;
    use=rhs.use;
    return *this;                   //返回本对象
}

```

> <font color=red>建议：</font>对于一个赋值运算符来说，正确工作是非常重要的。一个好的方法是在销毁左侧运算对象资源之前拷贝右侧运算对象

#### 13.3 交换操作

* 与拷贝控制成员不同，`swap`并不是必要的。但是，对于分配了资源的类，定义`swap`可能是一种很重要的优化手段
  * 在赋值运算符中使用`swap`，这种技术称为`拷贝并交换(copy and swap)`,使用拷贝并交换的赋值运算符是异常安全，且能正确处理自赋值(见例子一)

```cpp
//例子一：拷贝并交换
class HasPtr{
    friend void swap(HasPtr&,HasPtr&);
    //其他成员定义，与之前行为像指针的类的定义相同
};
inline
void swap(HasPtr &lhs,HasPtr &rhs){
    using std::swap;
    swap(lhs.ps,rhs.ps);        //交换指针，而不是string数据
    swap(lhs.i,rhs.i);          //交换int成员
}

//在本例中，使用swap函数进行赋值不会收益，因为这个版本的类不用进行内存分配，只是指针的交换
//拷贝并构造
HasPtr& HasPtr::operator=(HasPtr rhs){
    //rhs是一个副本，在函数结束后会被自行销毁
    swap(*this,rhs);            //rhs现在指向本对象曾经使用的内存
    return *this;               //rhs被销毁，从而delete了rhs中指针
}
```

#### 13.4 拷贝控制示例

(本节主要是编程实践)

#### 13.5 动态内存管理类

(本节主要是编程实践)

#### 13.6 对象移动

* `右值引用`:所谓右值引用就是必须绑定到右值的引用，通过`&&`来获得右值引用
  * 一般来说一个左值表达式表示的是一个对象的身份，而一个右值表达式表示的是对象的值
* 返回左值引用的函数，连同赋值、下标、解引用和前置递增/递减运算符，都是返回左值的表达式的例子
* 返回非引用类型的函数，连同算法、关系、位以及后置递增/递减运算符，都是生成右值。我们不能将左值引用绑定到这类表达式上，**但我们可以将一个`cosnt`的左值引用或者一个右值引用绑定到这类表达式上**.
* <font color=red>左值持久；右值短暂，这意味着使用右值引用的代码可以自由地接管所引用的对象的资源，因为右值本身是即将被销毁的对象</font>
* 可以通过名为`move`的新标准库函数来获得绑定到左值上的右值引用，此函数定义在头文件`utility`中
  * 对`move`我们不提供`using`声明，我们直接调用`std::move`而不是`move`
* 定义移动构造函数和移动赋值运算符的关键在于，一旦资源完成移动，源对象必须不再指向被移动的资源，这些资源的所有权已经归属于新创建的对象(见例子一)
  * 由于移动操作“窃取”资源，它通常不分配任何资源，因此移动操作通常不会抛出任何异常，此时我们可以将其声明为`noexcept`(`noexcept`出现在参数列表和初始化列表开始的冒号之间s)
  * 在移动操作之后，移后源对象必须保持有效的、可析构的状态，**但是用户不能对其值进行任何假设**
* 如果一个类定义了自己的拷贝构造函数、拷贝赋值运算符或者析构函数，编译器就不会为它合成移动构造函数和移动赋值运算符
  * 只有当一个类没有定义任何自己版本的拷贝控制成员，且类的每个非`static`数据成员都可以移动时，编译器才会为它合成移动构造函数或移动赋值运算符
* 新标准中定义了一种`移动迭代器(move iterator)`适配器，与其他迭代器不同，移动迭代器的解引用运算符生成一个右值引用，我们通过调用标准库`make_move_iterator`函数将一个普通迭代器转换为一个移动迭代器(见例子二)
* 区分移动和拷贝的重载函数通常有一个版本接受一个`const T&`，而另一个版本接受一个`T&&`
* 在新标准中，我们可以指定对象的成员函数中`this`的左值/右值属性，其定义方式与定义`const`成员函数相同，集在参数列表后放置一个`引用限定符`
  * 对于`&`限定的函数，我们只能将它用于左值；对于`&&`限定的函数，只能用于右值
  * 一个函数可以同时用`const`和引用限定。在此情况下，引用限定符必须跟随在`const`限定符之后
  * 如果我们定义两个或两个以上具有相同名字和相同参数列表的成员函数，就必须对所有函数都加上引用限定符，或者所有都不加（见例子四）


```cpp
//例子一：定义移动操作
class StrVec{
    public:
        StrVec(StrVec&&) noexcept;
        StrVec& operator=(StrVec&&) noexcept;
};

//不抛出异常的移动操作在类内类外都要标记为noexcept
StrVec::StrVec(StrVec &&s) noexcept:elemetns(s.elements),first_free(s.first_free),cap(s.cap){
    //令s进入这样的状态
    s.elements=s.first_free=s.cpp=nullptr;
}

StrVec& StrVec::operator=(StrVec&& rhs) noexcept
{
    if(this!=&rhs){
        free();
        elements=rhs.elements;
        first_free=rhs.first_free;
        cap=rhs.cap;
        //将rhs置于可析构状态
        rhs.elements=rhs.first_free=rhs.cpp=nullptr;
    }
}

//例子二：移动迭代器
//详细代码见《C++ primer》chapter13
void StrVec::reallocate(){
    //分配大小两倍于当前规模的内存空间
    auto newcapacity=size()?2*size():1;
    auto first=alloc.allocate(newcapacity);
    //移动元素
    auto last=uninitialized_copy(make_move_iterator(begin()),
                                    make_move_iterator(end()),
                                    first);
    free();                 //释放旧空间
    elements=first;         //更新指针
    first_free=last;
}

//例子三：利用this右值属性进行原址排序
class Foo{
    public:
        Foo sorted() &&;                //可用于可改变的右值
        Foo sorted() const &;           //可用于任何类型的Foo
    private:
        vector<int> data;
};

//本对象为右值，因此可以原址排序
Foo Foo::sorted() &&
{
    sort(data.begin(),data.end());
    return *this;
}
//本对象是const或是一个左值，哪种情况我们都不能对其进行原址排序
Foo Foo::sorted() const &{
    Foo ret(*this);                                 //拷贝一个副本
    sort(ret.data.begin(),ret.data.end());          //排序副本
    return ret;                                     //返回副本
}

retVal().sorted();                  //retVal()是一个右值，调用Foo::sorted() &&
retFoo().sorted();                  //retFoo()是一个左值，调用Foo::sorted() const &

//例子四：重载this左值和右值的函数
class Foo{
    public:
        Foo sorted() &&;
        Foo sorted() const;         //错误：必须加上引用限定符

        using Comp=bool(const int&,const int&);
        Foo sorted(Comp*);          //正确：不同的参数列表
        Foo sorted(Comp*) const;    //正确：两个版本都没有引用限定符
};
```

> <font color=red>注意：</font>如果一个成员函数有引用限定符，则具有相同参数列表的所有版本都必须有引用限定符