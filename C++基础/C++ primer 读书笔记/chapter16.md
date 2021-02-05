### chapter16 模板与泛型编程

#### 16.1 定义模板

* `函数模板`可以有两类，一类是`模板类型参数`，另一类是`非类型模板参数`。其中`非类型模板参数`表示一个值而非一个类型。（见例子一）
* 定义在类模板之外的成员函数就必须以关键字`template`开始，后接类模板参数列表
* 默认情况下，对于一个实例化了的类模板，其成员只有在使用时才被实例化
* 在类模板自己的作用域中，我们可以直接使用模板名而不提供实参（见例子三）
  * 当我们在类模板外定义其成员时，必须记住，我们并不在类的作用域中，直到遇到类名才表示进入类的作用域
* 当一个类包含一个友元声明时，类与友元各自是否是模板是相互无关的（模板中友元的声明见例子四）
* 默认情况下，c++语言假定通过作用域运算符访问的名字不是类型。因此，<font color=red>如果我们希望使用一个模板类型参数的类型成员，就必须显式告诉编译器该名字是一个类型</font>，我们通过使用关键字`typename`来实现这一点（见例子五）
* 就像我们能为函数参数提供默认实参一样，我们也可以提供`默认模板实参`
  * 与函数默认实参一样，对于一个模板参数，只有当它右侧的所有参数都有默认实参时，它才可以有默认实参。
  * 如果一个类模板为其所有模板参数都提供了默认实参，且我们希望使用这些默认实参，就必须在模板名之后跟一个空尖括号对(见例子六)
* 类模板中定义了一个函数模板，当在类模板外定义该函数模板时，类模板的参数列表在前面，后跟函数模板自己的模板参数列表。

```cpp
//例子一
//类型参数
template<typename T>
int compare(const T& v2,const T &v2){
    if(v1<v2) return -1;
    if(v2<v1) return 1;
    return 0;
}

cout<<compare(1,0)<<endl;       //T为int

//非类型参数
template<unsigned N,unsigned M>
int compare(const char (&p1)[N],const char (&p2)[M]){
    return strcmp(p1,p2);
}

compare("hi","mom");            //N实例haul为3，M实例化为4

//例子二：对任意大小的数组使用模板的常用两种方式:

//方式一
template<typename Array>
void print(const Array& arr){
    /* 通过数组别名arr对数组进行操作 */
}

//方式二
template<typename T,unsigned N>
void print(const T (&arr)[N]){
    /* 通过指针arr对数组进行操作 */
}

//例子三
template<typename T>
class BlobPtr{
    public:
        BlobPtr():curr(0){}
        //这里在类作用域内，可以直接使用模板名
        BlobPtr& operator++();
    private:
        std::size_t cur;;
};

//在类作用域外必须加上模板类型
template<typename T>
BlobPtr<T> BlobPtr<T>::operator++(int){
    /*... */
}

//例子四：模板中友元的声明

template<typename> class BlobPtr;   //前置声明，在Blob中声明友元所需要
template<typename> class Blob;      //运算符==中的参数所需要
template<typename T>
bool operator==(const Blob<T>&,const Blob<T>&);

template<typename T>
class Blob{
    //每个Blob实例将访问权限授予吸纳共同类型实例化的BlobPtr和相等运算符
    friend class BlobPtr<T>;
    friend bool operator==<T>(const Blob<T>&,const Blob<T>&);
};

//例子五：使用模板中类型的方法
template<typename T>
typename T::value_type
top(const T& c){
    if(!c.empty())
        return c.back();
    else
        //返回模板T中的value_type类型
        return typename T::value_type;
}

//例子六：所有模板参数都有默认实参的情况
template<class T=int>
class Numbers{
    public:
        Numbers(T v=0):val(v) {}
    private:
        T val;
};

Number<long double> lots_of_precision;
Number<> average_precision;     //空<>不能少，表示我们希望使用默认类型
```

#### 16.2 模板实参推断

* 将实参传递给带模板类型的函数形参时，能够自动引用的类型转换只有`const`转换及数组或函数到指针的转换(见例子一)
  * `const`转换：可以将一个非`const`对象的引用（或指针）传递给一个`const`的引用（或指针）形参
  * 数组或函数指针转换：**如果函数形参不是引用类型**，则可以对数组或函数类型的实参应用正常的指针转换。一个数组实参可以转换为一个指向其首元素的指针。类似的，一个函数实参可以转换为一个该函数类型的指针
* 在函数模板中若返回类型也是一个模板参数类型则不太容易声明,一种比较好的方式是使用尾置返回类型进行声明（见例子二）
* 对于函数模板调用进行类型推断，其中以下两类需要特别注意（见例子三）:
  * 从左值引用函数参数推断类型:当一个函数参数是一个引用时，`只能传递给它一个左值`.实参类型可以是`const`类型，也可以不是。**如果实参是`const`的，则`T`将被推断为`const`类型。**
  * 从右值引用函数参数推断类型:当一个函数参数是一个右值引用时，我们**一般**(例外的情况下面会说)传递给它一个右值。
* 例外的两个规则:
  * 规则一：`X& &`、`X& &&`和`X&& &`都折叠成类型`&&`
  * 规则二：类型`X&& &&`折叠成`X&&`
  * 上述两个规则导致了两个重要结果:
    * 如果一个函数参数是一个指向模板类型参数的右值引用（如,`T&&`），则它可以被绑定到一个左值；
    * 且如果实参是一个左值，则推断出的模板实参类型将是左值引用，且函数参数将实例化为一个（普通）左值引用参数（`T&`）（见例子四）


```cpp
//例子一：模板中类型的自动转换
template<typename T> T fobj(T,T);       //实参被拷贝
template<typename T> T fref(const T&,const T&);     //引用
string s1("a value");
const string s2("another value");
fobj(s1,s2);            //调用fojb(string,string);const被忽略
fref(s1,s2);            //调用fref(const string&,const string&) 将s1转换为cosnt时允许的
int a[10],b[42];
fobj(a,b);              //调用f(int*,int*);
fref(a,b);              //错误：数组类型不匹配

//例子二：在模板中声明返回类型

//尾置返回运行我们在参数列表之后声明返回类型
template<typename It>
auto fcn(It beg,It end) -> decltype(*beg)
{
    return *beg;
}

//使用remove_reference移除引用属性，同时获取其类型
template<typename It>
auto fcn2(It beg,It end) -> typename remove_reference<decltype(*beg)>::type{
    return *beg;
}

//例子三

//参数是左值引用的两种情况
template<typename T> void f1(T&);   //实参必须是一个左值
f1(i);      //i是一个int;模板参数类型T是int
f1(ci);     //ci是一个const int;模板参数类型T是const int
f1(5);      //错误：传递给一个&参数的实参必须是一个左值

template<typename T> void f2(const T&);
f2(i);      //i是一个int;模板参数T是int
f2(ci);     //ci是一个const int,但模板参数T是int
f2(5);      //一个const&参数可以绑定到一个右值；T是int

//例子四

//参数是右值引用的情况
template<typename T> void g(T&& val);
int i=0; const int ci=i;
g(i);       //模板参数类型T是int&;val是int&
g(ci);      //模板参数类型T是const int&;val是const int&
g(i*ci);    //模板参数类型T是int;val是int&&

//例子五：std::move的定义

template<typename T>
typename remove_reference<T>::type&& move(T&& t){
    return static_cast<typename remove_reference<T>::type&&>(t);
}

/*
    对std::move的分析:
    1.当传入move的是一个左值时，t推断为T&,此时可以使用static_cast显式地将一个左值转换为一个右值引用
    2.当传入move的是一个右值时，t推断为T&&,于是类型转换什么也不做
*/
```

#### 16.3 重载与模板

#### 16.4 可变参数模板

#### 16.5 模板特例化
