### 知识点1：转换函数,conversion function

```cpp
//例子
class Fraction
{
public:
    Fraction(int num,int den=1):m_numerator(num),m_denominator(den){}
    operator double() const { return (double)(m_numerator/m_denominator);}
private:
    int m_numerator;    //分子
    int m_denominator;  //分母
};
//使用
Fraction f(3,5);
double d=4+f;   //调用operator double() 将f转为double
```

* 转换函数既没有显式的返回类型，也没有形参, 而且必须定义成类的成员函数。
* 类型转换运算符通常不应该改变待转换对象的内容，因此，类型转换运算符一般被定义成`const`成员。
* 转换函数可以将类转为任意类型，只要该类型事先已经声明.

#### 补充:显式的转换函数

有时使用隐式的转换函数会产生意想不到的错误，为了避免这种错误的发生，C++新标准引入了**显式的类型转换函数**

```c++
class SmallInt{
public:
    SmallInt(int i=0):val(i){
        if(i<0 || i>255)
            throw std::out_of_range("bad SamlllInt value");
    }
    //编译器不会自动执行这一类型转换
    explicit operator int() const { return val; }
private:
    std::size_t val;
};

int main(){
    SmallInt si=3;  //正确:SmallInt的构造函数不是显式的
    si+=3;          //错误:此处需要影式的类型转换，但类的运算符是显式的
    static_cast<int>(si)+3;     //正确:显式地请求类型转换
}
```

### 知识点2：non-explicit-one-argument ctor & explicit-one-argument ctor

#### non-explicit-one-argument

```c++
class Fraction
{
public:
    Fraction(int num,int len=1):m_numerator(num),m_denominator(den) {}
    Fraction operator+(const Fraction& f){
        return Fraction(...);
    }
private:
    int m_numerator;
    int m_denominator;
};
//调用
int main(){
    Fraction f(3,5);
    Fraction d2=f+4;    //调用non-explicit ctor将4转为Fraction
                        //然后调用operator+
}
```

* 只有一个未初始化参数的non-explicit构造函数可以将其他类型转为当前类(和转换函数的功能刚好相反)

#### explicit-one-argument

```cpp
class Fraction
{
public:
    explicit Fraction(int num,int len=1):m_numerator(num),m_denominator(den) {}
    operator double() const{
        return (double)(m_numerator/m_denominator);
    }
    Fraction operator+(const Fraction& f){
        return Fraction(...);
    }
private:
    int m_numerator;
    int m_denominator;
};
//调用
int main(){
    Fraction f(3,5);
    Fraction d2=f+4;    //Error:conversion from 'double' to 'Fraction' requested
}
```

* `explicit`构造函数不能将其他类型隐式地转换为当前类


### 知识点3：智能指针

#### shared_ptr

```c++
//shared_ptr简化版
template <class T>
class shared_ptr{
public:
    //获取元素
    T& operator* const{
        return *px;
    }
    //获取指针
    T* operator-> const{
        return px;
    }
    shared_ptr(T* p):px(p) {}
private:
    T*      px;
    long*   pn;
};
//定义Foo类
struct Foo{
    ...
    void method(void) {...}
};
//调用
int main(){
    shared_ptr<Foo> sp(new Foo);
    Foo f(*sp);
    sp->method;     //相当于px->method,运算符'->'具有传递性
}
```

#### 迭代器

![avatar](../../image/c++_候捷_迭代器1.jpg)
![avatar](../../image/c++_候捷_迭代器2.jpg)


#### 总结

* 智能指针一般要重载`operator*`和`operator->`,且`operator*`用于获取元素,`operator->`用于获取元素的指针.


### 知识点4：成员模板 member template

```cpp
template <class T1,class T2>
struct pair{
    typedef T1 first_type;
    typedef T2 second_type;

    T1 first;
    T2 second;

    pair():first(T1()),second(T2()){}
    pair(const T1& a,const T2& b):first(a),seoncd(b) {}

    //类模板中可以有另外不同类型的类模板
    template<class U1,class U2>
    pair(const pair<U1,U2>& p):first(p.first),second(p.second()) {}
};
//调用
int main(){
    class Base1{};
    class Derived1:public Base1{};
    class Base2{};
    class Derived2:public Base2{};

    pair<Derived1,Derived2> p;
    pair<Base1,Base2> p2(p);  //pair<Base1,Base2> p2(pair<Derived1,Derived2>());
}
```







