### chapter7 仿函数


#### 仿函数概述

`仿函数`,后来也被称为`函数对象`,是一种具有函数特质的对象。任何应用程序欲使用STL内建的仿函数，都必须含入`<functional>`头文件，SGI则将它们实际定义于`stl_function.h`文件中。

`STL`仿函数以操作数划分，分为一元和二元仿函数，在`stl_functional.h`中定义了两个`class`分别代表一元仿函数和二元仿函数。


```cpp
template<class Arg,class Result>
struct unary_function{  //一元函数父类
    typedef Arg argument_type;
    typedef Result result_type;
};

template<class Arg1,class Arg2,class Result>
struct binary_function{ //二元函数父类
    typedef Arg1 first_argument_type;
    typedef Arg2 second_argument_type;
    typedef Result result_type;
};

//使用
template<class Predicate>
class unary_negate{
    //...
    public:
        bool operator()(const typename Predicate::argument_type& x) const {
            //...
        }
};
```

#### 仿函数分类

STL中定义的仿函数有:

* 算术类仿函数:加法`plus`,乘法`multiplies`等
* 关系运算类仿函数:大于`greater`,小于`less`等
* 逻辑运算类仿函数:逻辑与`logical_and`,逻辑或`logical_or`和逻辑非`logical_not`
* 证同、选择、投射:证同`identity`,选择`select1st/select2nd`,投影`project1st/project2nd`

部分函数实现如下所示:

```cpp
//plus
template<class T>
struct plus:public wj::binary_function<T,T,T>{
    T operator()(const T& x,const T& y) const { return x+y; }
};

//minus
template<class T>
struct minus:public wj::binary_function<T,T,T>{
    T operator()(const T& x,const T& y) const { return x-y; }
};

//multiplies
template<class T>
struct multiplies:public wj::binary_function<T,T,T>{
    T operator()(const T& x, const T& y) const { return x* y; }
};


//equal_to
template<class _Tp>
struct equal_to:public wj::binary_function<_Tp,_Tp,bool>
{
    bool operator()(const _Tp& _x,const _Tp& _y) const
    {
        return _x==_y;
    }
};

//select1st
template<class _Pair>
struct select1st:public unary_function<_Pair,_Pair>{
    const typename _Pair::first_type operator()(const _Pair& _x) const{
        return _x.first;
    }
};

//identity
template<class T>
struct identity:public unary_function<T,T>
{
    const T& operator()(const T& x) const { return x;}
};
```

