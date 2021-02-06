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

### 序列式容器vector

#### vector概述

`vector`与`arry`非常相似，不同之处在于`array`是静态空间，一旦大小设定就不能改变;而`vector`是动态空间，随着元素的加入，它的内部机制会自行扩充空间以容纳新元素。

#### vector的迭代器

`vector`维护的是一个连续线性空间，所以使用普通指针就可以作为`vector`的迭代器。所以`vectro`提供的是`Random Access Iterator`。

```cpp
template<class T,class Alloc=alloc>
class vector{
    public:
        typedef T           value_type;
        typedef value_type* iterator;       //vector的迭代器
};
```

#### vector的数据结构

`vector`所采用的数据结构非常简单：线性连续空间。它以两个迭代器`start`和`finish`表示目前使用空间的头尾，用`end_of_storage`指向整块连续空间的尾段.

```cpp
template<class T,class Alloc=alloc>
class vector{
    //...
    protected:
        iterator start;         //表示目前使用空间的头
        iterator finish;        //表示目前使用空间的尾
        iterator end_of_storage;//表示目前可用空间的尾
};
```

#### vector的构造与内存管理

当备用空间不足时，`vector`采用二倍扩充的方式重新配置，即`申请两倍大的新空间`、`移动数据`、`释放原空间`。采用这种方式，可以使得`push_back()`操作时间复杂度的平摊代价为`O(1)`, 其代码如下所示:

```cpp
template<class T,class Alloc>
void vector<T,Alloc>::insert_aux(iterator position,const T& x){
    if(finish!=end_of_storage){
        //还有备用空间
        //在备用空间起始处构造一个元素，并以vector最优一个元素值为其初值
        wj::construct(finish,*(finish-1));
        //调整水位
        ++finish;
        T x_copy=x;
        //将positionk和其后面元素的位置往后挪
        std::copy_backward(position,finish-2,finish-1);
        *position=x_copy;
    }
    else{
        //已无备用空间
        const size_type old_size=size();
        //采用二倍扩充的原则
        const size_type len=old_size!=0?2*old_size:1;
        iterator new_start=data_allocator::allocate(len);
        iterator new_finish=new_start;
        try{
            //复制前半段内容到新vector
            new_finish=std::uninitialized_copy(start,position,new_start);
            //为新元素设定初值x
            wj::construct(new_finish,x);
            ++new_finish;
            //复制后半段内容到新vector
            new_finish=std::uninitialized_copy(position,finish,new_finish);
        }
        catch(...){
            //处理异常
            wj::destory(new_start,new_finish);
            data_allocator::deallocate(new_start,len);
            throw;
        }
        //析构并释放原vector
        wj::destory(begin(),end());
        deallocate();
        //调整迭代器，指向新vector
        start=new_start;
        finish=new_finish;
        end_of_storage=new_start+len;
    }
}
```
