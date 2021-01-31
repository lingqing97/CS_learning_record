### chapter9 顺序容器

#### 9.1 顺序容器概述

|  | 顺序容器类型 | |
| :----: | :----: | :----: |
| vector | 可变大小数组，支持快速随机访问 | 在尾部之外的位置插入和删除元素可能很慢 |
| deque  | 双端数组,支持快速随机访问  | 在头尾位置插入/删除速度很快 |
| list  | 双向链表,只支持双向顺序访问  | 在list中任何位置进行插入/删除操作速度都很快 |
| forward_list  | 单向链表,只支持单向顺序访问  | 在链表任何位置进行插入/删除操作速度都很快 |
| array  | 固定大小数组，支持快速随机访问  | 不能添加或删除元素
| string  | 与vector类似的容器,但专门用于保存字符  | 随机访问快，在尾部/删除速度快

* 如果你不确定应该使用哪种容器，那么可以在程序中只使用`vector`和`list`公共的操作：使用迭代器，不使用下标操作，避免随机访问。这样，在必要时选择使用`vector`或`list`都很方便
* <font color=red>`array`可以进行拷贝和对象赋值操作</font>(见例子一)

```cpp
//例子一：
array<int,10> a1={0,1,2,3,4,5,6,7,8,9};
array<int,10> a1={0};               //所有元素值均为0
a1=a2;                              //替换a1中的元素
a2={0};                             //错误：不能将一个花括号列表赋予数组
```

#### 9.2 容器库概览

* 标准库中除了定义正向迭代器，还定义了反向迭代器，反向迭代器就是一种反向遍历容器的迭代器，对一个反向迭代器执行`++`操作，会得到上一个元素(见例子一)
  * `forward_list`不支持反向迭代器
* 将一个新容器创建为另一个容器的拷贝的方法有两种(见例子二):
  * 可以直接拷贝整个容器；当将一个容器初始化为另一个容器的拷贝时，两个容器的容器类型和元素类型都必须相同
  * 或者拷贝由一个迭代器对指定的元素范围（array除外）；范围拷贝时只需元素的类型能相互转换，容器类型和元素类型可以不同
* 顺序容器（除了`array`）还定义了一个名为`assign`的成员，允许我们从一个不同但相同的类型赋值，或者从容器的子序列赋值(见例子三)
* `swap`操作交换两个相同类型容器的内容
  * 除了`array`外，交换两个容器内容的操作保证会很快，因为元素本身并未交换，`swap`只是交换了两个容器的内部数据结构
* 除了`forward_list`,每个容器类型都有三个与大小相关的操作（`forward_list`只支持`max_size`和`empty`）:
  * `size()`返回容器中元素的数目
  * `empty()`当`size`为0时返回布尔值`true`
  * `max_size()`返回一个大于或等于该类型容器所能容纳的最大元素数的值

```cpp
//下面的例子都是所有容器（包括顺序容器和关联容器）都有的操作，特殊情况会标出

//例子一：容器库的迭代器相关操作
c.begin(),c.end()                   //返回指向c的首元素和尾元素之后位置的迭代器
c.cbegin(),c.cend()                 //返回const_iterator

c.rbegin(),c.rend()                 //返回指向c的尾元素和首元素之前位置的迭代器
c.crbegin(),c.crend()               //返回const_reverse_iterator

//例子二：容器定义和初始化
C c;                                //默认构造

C c1(c2)                            //拷贝，c1和c2必须相同容器类型和相同元素类型
                                    //     对于array类型还必须就有相同大小

C c{a,b,c,...}                      //列表初始化


C c(b,e)                            //范围拷贝，c初始化为迭代器b和e定义范围的元素的拷贝（array不适用）

vector<const char*> articles={"a","an","the"};
forward_list<string> words(articles.begin(),articles.end());

//例子三：顺序容器的assign操作
seq.assign(b,e)                     //将seq中的元素替换为迭代器b和e所表示范围中的元素。迭代器b和e不能指向seq中的元素
seq.assign(il)                      //将seq中的元素替换为初始化列表il中的元素
seq.assign(n,t)                     //将seq中的元素替换为n个值为t的元素
```

#### 9.3 顺序容器操作

* 向一个`vector`、`string`或`deque`插入元素会使所有指向容器的迭代器、引用或指针失效
* c++11新标准引入了三个新成员`emplace_front`、`emplace`和`emplace_back`，这些操作分别对应`push_front`、`insert`和`push_back`.
  * `emplace`成员函数，是将参数传递给元素类型的构造函数,传递给`emplace`函数的参数必须与元素类型的构造函数相匹配(见例子一)
* `insert`成员函数通过迭代器插入元素，有四个版本（见例子二）
  * 由于插入操作会改变容器的大小，所以不适用于`array`
* 除了`forward_list`没有`back`成员函数外，其他顺序容器都有`front`和`back`成员函数:
  * `front`返回容器首元素的引用
  * `back`返回容器尾元素的引用
* `erase`操作进行元素的删除，有两个版本（见例子三）
  * 由于删除操作会改变容器的大小，所以也不适用于`array`
* 由于`forward_list`是单向链表，删除和添加元素的操作不太一样，它定义了自己特殊的相关操作（见例子四）

```cpp
//例子一：emplace成员函数
c.emplace_back("978-058782323",25,15.99);
c.push_back("978-058782323",25,15.99);              //错误：没有接受三个参数的push_back版本
c.push_back(Sales_data("978-058782323",25,15.99));  //正确：创建一个临时的Sales_data对象传递给push_back

//例子二：insert成员函数
//forward_list有特殊版本的insert和emplace
//共性：都插入到迭代器p指向的元素之前,都返回指向新添加的第一个元素的迭代器
c.insert(p,t)                                       //在迭代器p指向的元素之前创建一个值为t或由args创建的元素。
c.emplace(p,args)                                   //返回指向新添加的元素的迭代器

c.insert(p,n,t)                                     //在迭代器p指向的元素之前插入n个值为t的元素。
                                                    //返回指向新添加的第一个元素的迭代器；若n为0，则返回p

c.insert(p,b,e)                                     //将迭代器b和e指定的范围内的元素插入到迭代器p指向的元素之前，b和e不能指向c中的元素
                                                    //返回指向新添加的第一个元素的迭代器；若范围为空，则返回p

c.insert(p,il)                                      //il是一个花括号包围的元素值列表。将这些给定值插入到迭代器p指向的元素之前
                                                    //返回指向新添加的第一个元素的迭代器；若列表为空，则返回p

list<string> lst;
auto iter=lst.begin();
while(cin>>word)
    iter=lst.insert(iter,word);                     //等价于调用push_front

//例子三：erase成员函数
//forward_list有特殊版本的erase
//共性：都返回最后一个被删除元素之后元素的迭代器
c.erase(p)                                          //删除迭代器p所指的元素，返回一个指向被删元素之后元素的迭代器

c.erase(b,e)                                        //删除迭代器b和e所指定范围内的元素，返回一个指向最后一个被删除元素之后元素的迭代器

//循环删除一个list中的所有奇数元素
list<int> lst={0,1,2,3,4,5,6,7,8,9};
auto it=lst.begin();
while(it!=lst.end()){       //lst.end()不能提前记录，因为删除的过程中迭代器会失效
    if(*it%2)
        it=lst.erase(it);
    else
        ++it;
}

//例子四：在forward_list中插入或删除元素的操作
lst.before_begin()                                  //返回指向链表首元素之前不存在的元素的迭代器，此迭代器不能解引用
lst.cbegin_begin()                                  //返回一个const_iterator

lst.insert_after(p,t)                               //在迭代器p之后的位置插入元素,犯规指向最优一个插入元素的迭代器
lst.insert_after(p,n,t)                             //t是一个对象，n是数量
lst.insert_after(p,b,e)                             //b和e是表示范围的一对迭代器
lst.insert_after(p,il)                              //il是一个花括号列表

lst.erase_after(p)                                  //删除p所指向的位置之后的元素
lst.erasea_after(b,e)                               //b和e是迭代器范围，返回一个指向被删元素之后元素的迭代器

//循环删除一个forward_list中的所有奇数元素
forward_list<int> flst={0,1,2,3,4,5,6,7,8,9};
auto prev=flst.begin_begin();                       //需要记录删除的前一个位置
auto curr=flst.begin();
while(curr!=flst.end()){
    if(*curr%2){
        //删除它并移动curr,prev不需要动
        curr=flst.eraser_after(prev);
    }
    else{
        //两个指针前移
        prev=curr;
        ++curr;
    }
}

//例子五：傻瓜循环，删除偶数元素，复制每个奇数元素
vector<int> lst={0,1,2,3,4,5,6,7,8,9};
auto iter=lst.begin();
while(iter!=lst.end()){
    if(*iter%2){
        iter=lst.insert(iter,*iter);                //复制当前元素
        iter+=2;                                    //向前移动迭代器，跳过当前元素以及插入到它之前的元素
    }
    else{
        iter=lst.erase(iter);                       //删除偶数元素
        //不应向前移动迭代器，iter指向我们删除的元素之后的元素
    }
}
```

> <font color=red>如果在一个循环中插入/删除deque、string或vector中的元素，不要缓存end返回迭代器</font>

#### 9.4 vector对象是如何增长的

* 容器的`size`是指它已经保存的元素的数量，而`capacity`则是在不分配新的内存空间的前提下它最多可以保存多少元素
  * 实际上，只要没有操作需求超出`vector`的容量，`vector`就不能重新分配内存空间

#### 9.5 额外的string操作

* 相比于其他容器，`string`还提供了其他额外的操作（见例子一）
  * `string`的每个搜索操作都会返回一个`string::size_type`值，表示匹配发生位置的下标。如果搜索失败，则返回一个名为`string::npos`的`static`成员

```cpp
//例子一
s.insert(pos,args)                  //在pos之前插入args指定的字符，pos可以是一个下标或一个迭代器
                                    //当pos是下标时，返回一个指向s的引用
                                    //当pos是迭代器时，返回指向第一个插入字符的迭代器

s.erase(pos,len)                    //删除从位置pos开始的len个字符,若len被省略，则删除从pos开始直至s末尾的所有字符
                                    //返回一个指向s的引用

s.find(args)                        //查找s中args第一次出现的位置
s.rfind(args)                       //查找s中args最后一次出现的位置

s.find_first_of(args)               //在s中查找args中任何一个字符第一次出现的位置
s.find_last_of(args)                //在s中查找args中任何一个字符最后一次出现的位置
s.find_first_not_of(args)           //在s中查找第一个不在args中的字符
s.find_last_not_of(args)            //在s中查找最后一个不在args中的字符


args必须是以下形式之一:
c,pos                               //从s中位置pos开始查找字符c,pos默认为0
s2,pos                              //从s中位置pos开始查找字符串s2,pos默认为0
cp,pos                              //从s中位置pos开始查找指针cp指向的以空字符串结尾的c风格字符串,pos默认为0
cp,pos,n                            //从s中位置pos开始查找指针cp指向的数组的前n个字符，pos和n无默认值

string name("AnnaBelle");
//pos=0
auto pos=name.find("Anne");

string numbers("0123456789"),name("r2d2");
//返回1，即name中第一个数字的下标
auto pos=name.find_first_of(numbers);

string dept("03714p3");
//返回5，即字符'p'的下标
auto pos=dept.find_first_not_of(numbers);

//在字符串中循环地搜索子字符串出现的所有位置
string::size_type pos=0;
while((pos=name.find_first_of(numbers,pos))!=string::npos){
    cout<<"found number at index:"<<name[pos]<<endl;
    ++pos;                          //移动到下一个字符
}
```

#### 9.6 容器适配器

* `适配器`是标准库中的一个通用概念，容器、迭代器和函数都有适配器
  * 例如`stack`适配器接受一个顺序容器（除`array`和`forward_list`外），并使其操作起来像一个`stack`一样
* 标准库定义了三个顺序容器适配器:`stack`、`queue`和`priority_queue`
  * `stack`默认基于`deque`实现，也可以在`list`或`vector`之上实现
  * `queue`默认基于`deque`实现
  * `priority_queue`默认基于`vector`实现

```cpp
//例子一：栈操作
s.pop()                             //删除栈顶元素，但不返回该元素值
s.push(item)                        //创建一个新元素压入栈顶
s.emplace(args)                     //通过args创建的元素压入栈顶
s.top()                             //返回栈顶元素，但不将元素弹出栈

//例子二：queue和priority_queue操作
q.pop()                             //删除queue的首元素或priority_queue的最高优先级的元素，但不返回此元素
q.front()                           //返回首元素或尾元素，但不删除此元素
q.back()                            //只适用于queue
q.top()                             //返回最高优先级元素，但不删除该元素，只适用于priority_queue
q.push(item)                        //压入新元素
q.emplace(args)

//在vector上实现的空栈
stack<string,vector<string>> str_stk;
//在str_stk2在vector上实现，初始化时保存svec的拷贝，svec是一个vector<string>
stack<string,vector<string>> str_stk2(svec);
```
