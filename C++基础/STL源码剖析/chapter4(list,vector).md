## chapter4 序列式容器(list,vector)


### 序列式容器list

#### list概述

`STL`中实现的`list`是数据结构中常提的`双向环状链表`。设计过`list`的人都知道，`list`本身和`list`所含的节点是不同的结构，需要分开设计。

其中`STL`中`list`的节点结构如下:

```cpp
    //定义链表节点
    template<class T>
    struct __list_node{
        __list_node* prev;          //指向上一个节点
        __list_node* next;          //指向下一个节点
        T data;
    };
```

#### list的迭代器

`list`由于是双向链表，所以其迭代器应该是双向迭代器`(BidirectionIterator)`，具有前移(`++`),后移(`--`)的能力。

下面以重载的`++`操作符为例进行说明:

```cpp
    //前置++
    self& operator++(){
        node=(*node).next;
        return *this;
    }
    //后置++
    self operator++(int){
        self tmp=*this;
        node=(*node).next;
        return tmp;

```

其中后置版`++`通过设置一个`int`型参数与前置版本`++`进行区分，且后置版本返回的是一个`值`,而前置版本返回的是一个`引用`。（关于c++的函数重载可以参考[《C++ primer》chapter14 读书笔记](https://blog.csdn.net/qq_39621037/article/details/113527686)）

这里需要特别注意的是后置版本`++`中的`self tmp=*this`语句，这条语句首先调用的是`iterator`的拷贝构造函数`ctor`,并且以`*this`作为实参，而不是调用重载的`operator*`。

以下是`list`迭代器的完整设计:

```cpp
//定义链表迭代器
template<class T,class Ref,class Ptr>
struct __list_iterator{

    //下面两个声明其实作用是一样的，只是会为后面代码的可读性
    typedef __list_iterator<T,T&,T*>        iterator;
    typedef __list_iterator<T,Ref,Ptr>      self;

    //这里未继承iterator,所以显示定义迭代器的五种相应类别
    typedef T                               value_type;
    typedef Ptr                             pointer;
    typedef Ref                             reference;
    typedef ptrdiff_t                       difference_type;
    typedef wj::bidirectional_iterator_tag  iterator_category;

    typedef __list_node<T>* link_type;
    typedef size_t size_type;

    //指向一个链表节点
    link_type node;

    //定义ctor
    __list_iterator(){}
    __list_iterator(link_type x):node(x){}
    __list_iterator(const iterator& x):node(x.node){}

    //重载相关操作
    bool operator==(const iterator& x) const { return node==x.node; }
    bool operator!=(const iterator& x) const { return node!=x.node; }
    reference operator*() const { return (*node).data; }
    pointer operator->() const { return &(operator*()); }
    self& operator++(){
        node=(*node).next;
        return *this;
    }
    self operator++(int){
        self tmp=*this;
        node=(*node).next;
        return tmp;
    }
    self& operator--(){
        node=(*node).prev;
        return *this;
    }
    self operator--(int){
        self tmp=*this;
        node=(*node).prev;
        return tmp;
    }
};
```

#### list的数据结构

`SGI STL`中实现的不仅仅是一个双向链表，而且还是一个环状双向链表，其实现只利用了一个`node`指针。

`node`指针是一个占位用的指针，其`next`指针指向环状双向链表的头部，而其`prev`指针则指向环状双向链表的尾部。

```cpp
template<class T,class Alloc=wj::alloc<__list_node<T>>>
class list{
    protected:
        typedef __list_node<T> list_node;
        //...
    public:
        typedef list_node* link_type;
        //...
    protected:
        //使用一个指针，便可表示整个环状双向链表
        link_type node;
        //...
};
```

从上述代码可以看出，`SGI STL`中的`list`仅使用一个指针便表示出整个链表，所以链表本身占用的空间只有`4字节(32位机器)`（但在后来的版本中链表有`8字节`）。

`list`的核心操作由插入`insert`,删除`erase`,迁移`transfer`（这里所谓的迁移操作，是将某连续范围的元素迁移到某个特定位置之前）等，大部分属于数据结构方面的知识，这里不再赘述。

#### 最后

本节中涉及的代码及本人实现的toy级别的`list`可以参考[github](https://github.com/lingqing97/tinySTL/blob/master/stl_wj_list.h).
