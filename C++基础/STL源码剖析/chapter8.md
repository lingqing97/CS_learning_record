### chapter8 配接器

#### 配接器概述

STL提供的配接器可以分为三类:

1. `iterator adapter`:改变迭代器的接口
2. `container adapter`:改变容器接口
3. `function adapter`:改变仿函数的接口


#### iterator adapter

在STL中`iterator adapter`又可以分为三类:

1. `insert iterators`:包括`back_inserter`,`front_inserter`和`inserter`三种
2. `reverse iterator`:将迭代器的移动行为倒转
3. `stream iterators`:将迭代器绑定到一个`strem`(数据流)对象身上

`insert iterators`实际上是对容器的一种封装，其中`back_inserter`实际是调用底层容器的`push_back()`接口,`front_inserter`实际是调用底层容器的`push_front()`接口，而`inserter`实际是调用底层容器的`insert()`接口。

`inserter iterators`的部分实现如下:

```cpp
//back_inserter在STL中调用模板类back_insert_iterator实现
template<class Container>
class back_insert_iterator{
    protected:
        Container* container;       //底层容器
    //...
    public:
        explicit back_insert_iterator(Container& x):container(x) {}
        //关键所在
        back_insert_iterator<Container>&
        operator=(const typename Container::value_type& value){
            container->push_back(value);
            return *this;
        }
    //...
};
//...
```

`reverse iterator`将迭代器的移动行为倒装，其底层将正向迭代器的`++`当做`--`，`--`当做`++`,所以使用`reverse iterator`必须至少是`Bidirectional Iterator`.

其部分重要实现如下:

```cpp
//reverse_iterator
//是前进为后退，后退为前进
template<class Iterator>
class reverse_iterator{
    protected:
        Iterator current;   //记录对应之正向迭代器
    //...
    public:
        typedef Iterator iterator_type;
        explicit reverse_iterator(iterator_type x):current(x) {}
        //关键所在
        reference operator*() const{
            Iterator tmp=current;
            return *--tmp;
        }
        //前进变后退
        self& operator++(){
            --current;
            return *this;
        }
        //后退变前进
        self& operator--(){
            ++current;
            return *this;
        }
    //...
};
```

`stream iterators`的实现是通过底层绑定一个`stream object`.(思想值得借鉴)

对于`istream_iterator`是通过绑定一个`istream objects`,客户端对这个迭代器所做的`operator++`操作，会被导引调用迭代器内部所含的那个`istream member`的输入操作(`operator>>`),这个迭代器是`Input iterator`,不具备`operator--`;

其部分实现如下:

```cpp
//istream_iterator
template<class T,class Distance=ptrdiff_t>
class istream_iterator
{
    //...
    protected:
        istream* stream;    //底层stream object
        T value;            //记录读取的值
        bool emd_marker;
        void read(){
            end_marker=(*stream)?true:false;
            if(end_marker) *stream>>value;
            end_marker=(*stream)?true:false;
        }
    public:
        //...
        istream_iterator():stream(&cin),end_marker(false){}
        //这里设计的有缺陷:
        //  istream_iterator<int> eos;      //造成end_marker为false
        //  istream_iterator<int> initer(cin);  //引发read()
        //  cout<<"please input..."<<endl;      //直到read()执行完，即输入数据后，该语句才会输出
        istream_iterator(istream& s):stream(&s) { read(); }

        typedef conat T&        reference;
        reference operator* const { return value; }

        //迭代器前进一个位置，就代表读取一笔资料
        istream_iterator<T,Distance>& operator++(){
            read();
            return *this;
        }

        //...
};
```

`ostream_iterator`在底层绑定一个`ostream object`,客户端对这个迭代器所做`operator=`操作，会调用`ostream memeber`的输出操作(`operator<<`),这个迭代器是个`OutputIterator`

其部分实现如下:

```cpp
//ostream_iterator
template<class T>
class ostream_itreator{
    protected:
        ostream* stream;
        const char* string;         //每次输出后的间隔符号
    public:
        //...
        ostream_iterator(ostream& s):stream(&s),string(0) {}
        ostream_iterator(ostream& s,const char& c):stream(&s),string(c) {}

        ostream_iterator<T>& operator=(const T& value){
            *stream<<value;
            if(string) *stream<<string;
            return *this;
        }

        ostream_iterator<T>& operator*() { return *this;}
        ostream_iterator<T>& operator++() { return *this; }
        ostream_iterator<T>& operator++(int) { return *this; }

        //...
};
```

#### container adapters

`container adapters`包括`stack`和`queue`,在之前的容器部分讨论过，这里不再赘述。

#### function adapters

`function adapters`内部也藏了一个`member object`,其型别等同于它所要配接的对象（那个对象当然是一个“可配接的仿函数”,adaptable functor）.当`function adatper`有了完全属于自己的一份修饰对象在手，它就成了该修饰对象的主人，也就有资格调用该修饰对象，并在参数和返回值上面动手脚。

下面以`binder1st`为例（在c++11中是`bind`）

```cpp
//binder1st
template<class Operation>
class binder1st:public unary_function<typename Operation::second_argument_type,
                                        typename operator::result_type>
{
    protected:
        Operation op;   //内部成员
        typename Operation::first_argument_type value;
    public:
        binder1st(const Operation& x,
                    const typename Operation::first_argument_type& y):op(x),value(y){ }

        //这是关键
        typename Operation::result_type
        operator()(const typename Operation::second_argument_type& x) const{
            return op(value,x);
        }
};
```

