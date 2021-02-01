### chapter12 动态内存

#### 12.1 动态内存与智能指针

* c++中内存可以划分为`静态内存`,`栈内存`和`堆`:
  * `静态内存`用来保存局部`static`对象、类`static`数据成员以及定义在任何函数之外的变量，由编译器自动创建和销毁
  * `栈内存`用来保存定义在函数内的非`static`对象，由编译器自动创建和销毁
  * `堆`用来存储`动态分配`的对象，即那些杂程序运行时分配的对象，动态对象的生存期由程序来控制，当动态对象不再使用时，我们的代码必须显式地销毁它们
* 为了更容易（同时也更安全）地使用动态内存，c++新标准提供了两种`智能指针`,它们复杂自动释放所指向的对象,它们都定义在头文件`memory`中
  * `shared_ptr`允许多个指针指向同一个对象（标准库还定义了`weak_ptr`的伴随类，它是一种弱引用，指向`shared_ptr`所管理的对象）
  * `unique_ptr`则“独占”所指向的对象
* 智能指针的使用与普通指针类似
  * 解引用一个智能指针返回它所指向的对象
  * 如果在一个条件判断中使用智能指针，效果就是检测它是否为空
* 最安全的分配和使用动态内存的方法是调用一个名为`make_shared`的标准库函数
  * `make_shared`函数在动态内存中分配一个对象并初始化它，返回指向此对象的`shared_ptr`,此函数定义在头文件`memory`中
* 一旦一个`shared_ptr`的计数器变为0，它就会自动释放自己所管理的对象
* 在`delete p`之后，指针`p`就变成了人们所说的`空悬指针`，即指向一块曾经保存数据对象但现在已经无效的内存的指针,可以在`delete`之后将`nullptr`赋予指针，这样清楚地指出指针不指向任何对象
* 如果使用智能指针管理的资源不是`new`分配的内存，记住传递给它一个删除器（见例子四）
* 当我们定义一个`unique_ptr`时，需要将其绑定到一个`new`返回的指针上
  * `unique_ptr`也可以通过普通指针初始化，不会有语法错误，但是会有后续的程序错误，所以强烈建议不要用普通指针初始化
  * <font color=red>由于一个`unique_ptr`拥有它指向的对象，因此`unique_ptr`不支持普通的拷贝或赋值操作</font>(见例子五)
  * 不能拷贝`unique_ptr`的规则有一个例外：我们可以拷贝或赋值一个将要被销毁的`unique_ptr`；最常见的例子就是从函数返回一个`unique_ptr`(见例子七)
* `weak_ptr`是一种不控制所指对象生存期的智能指针，它指向由一个`shared_ptr`管理的对象(只能指向`shared_ptr`)(`weak_ptr`的用法见例子九)
  * 将一个`weak_ptr`绑定到一个`shared_ptr`不会改变`shared_ptr`的引用计数
  * 一旦最后一个指向对象的`shared_ptr`被销毁，对象就会被释放，即使有`weak_ptr`指向对象，对象也还是会被释放
  * 在使用`weak_ptr`之前需要判断其所指的对象是否还存在，即使用`lock()`进行判断

```cpp
//例子一：shared_ptr的操作
make_shared<T>(args)                        //返回一个shared_ptr,指向一个动态分配的类型为T的对象，使用args初始化此对象

shared_ptr<T> p(q)                          //p是shared_ptr q的拷贝；此操作会递增q中的计数器。q中的指针必须能转换为T*

p=q                                         //p和q都是shared_ptr,此操作会递减p的引用计数，递增q的引用计数
                                            //若p的引用计数变为0，则将其管理的原内存释放

p.unique()                                  //若p.use_count() 为1，返回true;否则返回false

p.use_count()                               //返回与p共享对象的只能指针数量；可能很慢，主要用于调试

p.get()                                     //返回p中保存的指针。要小心使用，若指针指针释放了其对象，返回的指针所指向的对象也就消失了

//例子二：定义和改变shared_ptr的其他方法
shared_ptr<T> p(q)                          //q指向new分配的内存，并且能转换为T*类型
shared_ptr<T> p(u)                          //p从unique_ptr u哪里接管了对象的所有权；并将u置空
shared_ptr<T> p(q,d)                        //p将调用可调用对象d来代替delete

p.reset()                                   //是否p对ptr的所有权，若p是唯一指向其对象的shared_ptr,reset会释放此对象
p.reset(q)                                  //令p指向q
p.reset(q,d)                                //调用d而不是delete来释放q

//例子三
shared_ptr<int> p1=new int(1024);           //错误：由于shared_ptr的构造函数是explict，所以指针不能隐式转为shared_ptr
shared_ptr<int> p2(new int(1024));          //正确：使用了直接初始化形式

//例子四：自定义删除shared_ptr的删除操作
shared_ptr<int> sp(new int[10],[](int *p) { delete []p; });

//例子五：unique_ptr的初始化
unique_ptr<string> p1(new string("Stegosaurus"));
unique_ptr<string> p2(p1);                  //错误：unique_ptr不支持拷贝
unique_ptr<string> p3;
p3=p2;                                      //错误：unique_ptr不支持赋值

//例子六：unique_ptr操作
unique_ptr<T> u1                            //空unique_ptr,可以指向类型为T的对象。u1会使用delete来释放它的指针
unique_ptr<T,D> u2                          //u2会使用一个类型为D的可调用对象来释放它的指针
unique_ptr<T,D> u3(p,d)                     //用类型为D的对象d代替delete

unique_ptr<T[]> u                           //u可以指向一个动态分配的数组，数组元素类型为T
unique_ptr<T[]> u(p)                        //u指向内置指针p所指向的动态分配的数组，p必须能转换为类型T*

u=nullptr                                   //释放u指向的对象，将u置为空
u.release()                                 //u放弃对指针的控制权，返回指针，并将u置为空（并不会释放指针所指内存，知识放弃控制权）
u.reset()                                   //释放u指向的对象
u.reset(q)                                  //令u指向内置对象q

//例子七：从函数返回一个unique_ptr
unique_ptr<int> clone(int p){
  //正确：从int*创建一个unique_ptr<int>
  return unique_ptr<int>(new int(p));
}

//例子八：自定义删除unique_ptr的删除操作
unique_ptr<objT,delT> p(new objT,fcn);

//例子九：weak_ptr操作
weak_ptr<T> w                               //空weak_ptr可以指向类型为T的对象
weak_ptr<T> w(sp)                           //与shared_ptr sp指向相同对象的weak_ptr。T必须能转换为sp指向的类型

w=p                                         //p可以是一个shared_ptr或一个weak_ptr。赋值后与p共享对象

w.reset()                                   //将w置为空
w.use_count()                               //与w共享对象的`shared_ptr`的数量
w.expired()                                 //若w.use_count()为0，返回true，否则返回false
w.lock()                                    //如果expired为true,返回一个空shared_ptr；否则返回一个指向w的对象的shared_ptr

auto p=make_shared<int>(42);
weak_ptr<int> wp(p);                        //wp弱共享p；p的引用计数未改变
if(shared_ptr<int> np=wp.lock())            //使用weak_ptr的正确方式
{
  //在if中，np与p共享对象
}
```

> <font color>建议：</font>除非使用智能指针来管理内存，否则不要分配动态内存

#### 12.2 动态数组

* `new`运算将`内存分配`和`对象构造`组合在了一起，同理`delete`将`对象析构`和`内存释放`组合在了一起，这使得它们具有一些局限性
* 标准库`allocator`类定义在头文件`memory`中，它帮助我们将`内存分配`和`对象构造`分类开来(`allocator`的使用见例子一)
  * 标准库还未`allocator`类定义了两个伴随算法，可以在未初始化内存中创建对象(见例子二)

```cpp
//例子一：allocator类的正确使用

//step1:初始化，申请内存
allocator<string> alloc;                    //可以分配string的allocator对象
auto const p=alloc.allocate(n);             //分配n个未初始化的string,p指向分配的首地址

//step2:构造对象

auto q=p;
alloc.construct(q++);                       //*q为空字符串
alloc.construct(q++,10,'c');                //*q为cccccccccc
alloc.construct(q++,"hi");                  //*q为hi

//还未构造对象的情况下就使用原始内存是错误的
//cout<<*p<<endl;                           //正确：使用string的输出运算符
//cout<<*q<<endl;                           //灾难：q指向未构造的内存

//step3:析构对象
while(q!=p)
  alloc.destory(--q);                       //释放我们真正构造的string

//step4:释放内存
alloc.deallocate(p,n);


//例子二：allocator算法
uninitialized_copy(b,e,b2)                  //从迭代器b和e指出的输入范围中拷贝元素到迭代器b2指定的为构造的原始内存中,b2指向的内存必须足够大

uninitialized_copy_n(b,n,b2)                //从迭代器b指向的元素开始，拷贝n个元素到b2开始的内存中

uninitialized_fill(b,e,t)                   //在迭代器b和e指定的原始内存范围中创建对象，对象的值均为t的拷贝

uninitialized_fill_n(b,n,t)                 //从迭代器b指向的内存地址开始创建n个对象，b必须指向足够大的未构造的原始内存

allocator<string> alloc;
auto p=alloc.allocate(vi.size()*2)
//通过拷贝vi中的元素来构造从p开始的元素,返回指向最后一个构造的元素之后的位置的指针
auto q=uninitialized_copy(vi.begin(),vi.end(),p);
//将剩余元素初始化为42
uninitialized_fill_n(q,vi.size(),42);
```

#### 12.3 使用标准库：文本查询程序

(这节主要是编程实践)