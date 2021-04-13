## Day-8

### 问题

> 讲讲你理解的c++四大智能指针

### 参考答案

参考:

1. [C++里面的四个智能指针](https://blog.csdn.net/Poo_Chai/article/details/94733360)
2. [C++中的四个智能指针 博客园](https://www.cnblogs.com/xiaobaizzz/p/12167393.html)
3. [Auto_ptr被废弃的原因](https://blog.csdn.net/hyl999/article/details/106091299)

智能指针实际上是实现了`RAII`思想:资源在构造期间获得，在析构期间释放。将智能指针实现为一个类，在这个类构造时申请空间，当这个类离开作用域时，析构函数被调用从而使得申请的空间自动释放，尽可能地避免了内存泄露。

c++中有四个智能指针：`auto_ptr`、`unique_ptr`、`shared_ptr`和`weak_ptr`,其中`auto_ptr`已经被c++11弃用，而后三个在c++11中支持。

#### auto_ptr

`auto_ptr`采用**所有权模式**，对于特定的对象，只能有一个指针可以拥有。赋值操作会将所有权转移。

```cpp
auto_ptr<string> p1(new string("hello world!"));    //使用智能指针一般在构造函数中申请空间
auto_ptr<string> p2=p1;
cout<<*p2<<endl;
cout<<*p1<<endl;    //报错：此时p1已经失去了对内存的所有权
```

##### PS: auto_ptr被弃用的原因


`auto_ptr`在c++11中被弃用的原因是：当两个`auto_ptr`指针都指向同一个堆空间时，每个指针析构时都会`delete`这个堆空间，这会导致未定义行为。


#### unique_ptr

`unique_ptr`采用**独占式拥有，保证同一时间只有一个智能指针可以指向该对象**。

另外，`unique_ptr`设计更加精妙的地方在于：`unique_ptr`允许对临时右值进行拷贝赋值，而不允许对其他长时间存在的值进行拷贝赋值。

```cpp
unique_ptr<string> p1(new string("hello world!"));
//unique_ptr<string> p2=p1;               //报错,p1是一个长时间存在的左值，不允许拷贝赋值
unique_ptr<string> p3=std::move(p1);    //允许对临时右值进行拷贝赋值
```

#### shared_ptr

`shared_ptr`实现**共享式拥有，多个指针可以指向相同对象**。它通过引用计数来统计资源被几个指针共享，当引用指针减为0时，资源会被释放。

```cpp
shared_ptr<string> p1=make_shared<string>("hello world!");
shared_ptr<string> p2=p1;
cout<<*p1<<endl;            //输出:hello world!
cout<<*p2<<endl;            //输出:hello world!
cout<<p1.use_count()<<endl; //输出:2
p1.reset();                 //释放所有权
cout<<p2.use_count()<<endl; //输出:1
```

#### weak_ptr

`weak_ptr`是一种不控制所指向对象生存期的智能指针，它指向一个`shared_ptr`管理的对象，但该`weak_ptr`的构造和析构不会影响`shared_ptr`的引用计数。`weak_ptr`可以配合`shared_ptr`一起使用，从而解决`shared_ptr`相互引用时的死锁问题。

下面的代码摘自参考[2](https://www.cnblogs.com/xiaobaizzz/p/12167393.html)中的`shared_ptr`循环引用小节(具体可以参考原文)。

```cpp
#include<iostream>
#include<memory>
using namespace std;

class ListNode{
public:
	int m_value;
	shared_ptr<ListNode> prev;
	shared_ptr<ListNode> next;
	//构造函数
	ListNode(int value):m_value(value){
		cout << "constructor called!" <<endl;
	}
	//析构函数
	~ListNode(){
		cout << "destructor called!" <<endl;
	}
};

void test(){
	shared_ptr<ListNode> sp1 = make_shared<ListNode>(33);
	shared_ptr<ListNode> sp2 = make_shared<ListNode>(44);
	cout << sp1.use_count() << endl;
	cout << sp2.use_count() << endl;
	sp1 -> next = sp2;
	sp2 -> prev = sp1;
	cout << sp1.use_count() << endl;
	cout << sp2.use_count() << endl;
}

int main(){
	test();
	return 0;
}
//运行结果：
constructor called!
constructor called!
1
1
2
2
```

使用`weak_ptr`解决循环引用:

```cpp
#include<iostream>
#include<memory>
using namespace std;

class ListNode{
public:
	int m_value;
	weak_ptr<ListNode> prev;
	weak_ptr<ListNode> next;
	//构造函数
	ListNode(int value):m_value(value){
		cout << "constructor called!" <<endl;
	}
	//析构函数
	~ListNode(){
		cout << "destructor called!" <<endl;
	}
};

void test(){
	shared_ptr<ListNode> sp1 = make_shared<ListNode>(33);
	shared_ptr<ListNode> sp2 = make_shared<ListNode>(44);
	cout << sp1.use_count() << endl;
	cout << sp2.use_count() << endl;
	sp1 -> next = sp2;
	sp2 -> prev = sp1;
	cout << sp1.use_count() << endl;
	cout << sp2.use_count() << endl;
}

int main(){
	test();
	return 0;
}
//运行结果：
constructor called!
constructor called!
1
1
1
1
destructor called!
destructor called!
```