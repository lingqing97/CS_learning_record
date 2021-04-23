## Day-15

### 问题

> new和malloc的区别?

### 参考答案

参考:

1. [细说new与malloc的10点区别](https://www.cnblogs.com/qg-whz/p/5140930.html)
2. [malloc和new的区别](https://www.jianshu.com/p/8a5b5ee5c4d0)
3. [【C++】new和malloc的区别](https://zhuanlan.zhihu.com/p/47089696)
4. [经典面试题之new和malloc的区别](https://blog.csdn.net/nie19940803/article/details/76358673)
5. [理解C++ new-handler机制](https://blog.csdn.net/qilimi1053620912/article/details/89361479)
6. [C++中delete和delete[]的区别](https://www.cnblogs.com/charley_yang/archive/2010/12/08/1899982.html)

new和malloc主要有以下几点区别:

#### 1. new会调用对象的构造函数完成对象的构造；而malloc不会，这也是两者最大的区别

```cpp
class A{
    public:
        A(int a=1):_a(a) { cout<<"call A:A()"<<endl; }
    private:
        int _a;
};

int main(void)
{
    cout<<"construct ap1:";
    A* ap1=new A();
    cout<<"construct ap2:";
    A* ap2=(A*) malloc(sizeof(A));
    return 0;
}
/* 输出:
construct ap1:call A:A()
construct ap2:
*/
```

从这个例子可以非常直观地看到使用malloc不会调用对象的构造函数.

#### 2. new操作符从`自由存储区`上为对象分配内存空间，使用delete释放；而malloc从`堆`上为对象分配内存空间，使用free释放

`自由存储区`是C++基于`new`操作符的一个抽象概念，凡是通过`new`申请到的内存，这块内存就被称为`自由存储区`。

`堆`是操作系统层面上的概念，是操作系统所维护的一块特殊内存，用于程序的动态内存分配。

`自由存储区`可以是堆，也可以不是，这取决于具体实现。（默认情况下C++编译器会使用堆来实现自由存储）

#### 3. 内存分配失败时的处理策略不同: new操作符在内存分配失败时会抛出`bad_alloc`异常，它不会返回NULL；malloc在内存分配失败时返回NULL

new和malloc在`系统内存不足`或`超出进程的内存分配限制`时会导致内存分配失败。

new操作符在内存分配失败时，会抛出异常,通过捕获异常来判断内存分配是否成功。new操作符在抛出异常之前，会先调用一个用户指定的错误处理函数，这就是所谓`new-handler`处理机制（具体参考[理解C++ new-handler机制](https://blog.csdn.net/qilimi1053620912/article/details/89361479)）。

malloc在内存分配失败时，返回NULL,通过比较返回值是否是NULL判断内存分配是否成功。

```cpp
//捕获malloc内存分配失败的方式
int* p1=(int*)malloc(sizeof(int));
if(p1==NULL){
    cout<<"分配内存失败"<<endl;
    exit(1);
}

//捕获new内存分配失败的方式
try{
    int* p2=new int();
}
catch(bad_alloc){
    cout<<"分配内存失败"<<endl;
    exit(1);
}
```

#### 4. 申请数组时的操作不同: 使用new[]一次分配所有内存，多次调用构造函数。而malloc通过malloc(sizeof(obj)*n)分配所有内存

需要注意的是`new[]`需要和`delete[]`配合使用，防止出现内存泄露。

使用`new[]`分配数组时:对于基本数据类型，使用`delete[]`或`delete`都行；但是对于自定义数据类型，必须使用`delete[]`,否则会出现内存泄露。

```cpp
class A{
    public:
        A(int a=1):_a(a) { cout<<"call A:A()"<<endl; }
        ~A() { cout<<"call A:~A()"<<endl; }
    private:
        int _a;
};

int main(void){
    A* ap3=new A[5];
    cout<<"delete ap3:"<<endl;
    delete []ap3;

    // A* ap4=new A[5];
    // cout<<"delete ap4:"<<endl;
    // delete ap4;      //报错

    int* p3=new int[5];
    cout<<"delete p3:"<<endl;
    delete []p3;

    int* p4=new int[5];
    cout<<"delete p4:"<<endl;
    delete p4;  //对于基本类型可以，但不推荐

    return 0;
}
/*输出:
call A:A()
call A:A()
call A:A()
call A:A()
call A:A()
delete ap3:
call A:~A()
call A:~A()
call A:~A()
call A:~A()
call A:~A()
delete p3:
delete p4:
*/
```

#### 5. malloc分配的内存不足时，可以用realloc扩容；而new没有这样的配套设施

#### 6. new操作符可以重载；而malloc是库函数，不能重载

#### 7. new分配内存按照数据类型进行分配,返回指定对象的指针；malloc分配内存按照指定的大小分配，返回void*指针

### 追问: new/delete的功能完全覆盖了malloc/free,为什么还需要malloc和free?


