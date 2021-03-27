## Day-3

### 问题

> 请说出static尽可能多的作用

### 参考答案

参考:[C++中static关键字的总结](https://www.cnblogs.com/beyondanytime/archive/2012/06/08/2542315.html)

C++中`static`关键字的作用可以分为以下五类:

1. 面向过程中的作用
    * 静态局部变量
    * 静态全局变量
    * 静态函数

2. 面向对象中的作用
    * 静态成员变量
    * 静态成员函数

#### 面向过程中的作用

先看下面的例子:

```cpp
#include<iostream>

static void fn1();   //声明静态函数

static int n=0;     //声明静态全局变量

static void fn1()   //定义静态函数 ,static可有可无
{
    printf("a static global funciton.\n");
}

void fn2()
{
    ++n;
    printf("n=%d\n",n);
}

void fn3()
{
    if(1){
        static int p=1;   //静态局部变量
        ++p;
        printf("p=%d\n",p);
    }
    //printf("p=%d\n",p);
    //                ^
    //        error: ‘p’ was not declared in this scope
}

/*
输出:
a static global funciton.
n=20
n=21
p=2
p=3
*/

int main()
{
    n=20;
    fn1();
    printf("n=%d\n",n);
    fn2();
    fn3();
    fn3();
    return 0;
}
```

##### 静态局部变量

静态局部变量有以下特点:

1. 始终驻留在全局数据区，直到程序运行结束，**但其作用域为局部作用域，当定义它的函数或语句块结束时，其作用域随之结束**
2. 静态局部变量如果没有显示初始化，会被程序自动初始化为0

##### 静态全局变量

静态全局变量有以下特点:

1. 始终驻留在全局数据区，直到程序运行结束，**静态全局变量在声明它的整个文件都是可见的，而在文件之外则是不可见的**
2. 未初始化的静态全局变量会被程序自动初始化为0

> 全局变量同样驻留在全局数据区，其对所有文件都是可见的

##### 静态函数

静态函数与普通函数的不同在于：**静态函数不能被其它文件所用,所以不会与其它文件中同名的函数发生冲突**.

总结，在面向过程中，`static`关键字最重要的作用是**限制了其作用域**.

#### 面向对象中的作用

也是先看一个例子:

```cpp
#include<iostream>

class Myclass
{
    private:
        int a,b,c;
        static int d;                   //声明静态成员变量
    public:
        Myclass(int aa=0,int bb=0,int cc=0):a(aa),b(bb),c(cc){}
        int getsum() const;
        static int getsum_static();     //声明静态成员函数
};

int Myclass::d=0;                       //初始化静态成员变量

int Myclass::getsum() const
{
    ++d;
    printf("%d\n",a+b+c+d);
    printf("%d\n",d);
    return d;
}

int Myclass::getsum_static()            //不需要在声明关键字static
{
    //printf("%d\n",a+b+c+d);
    ++d;
    printf("%d\n",d);
    return d;
}

/*
输出:
7
1
14
2
3
4
*/

int main()
{
    Myclass class1(1,2,3);
    Myclass class2(3,4,5);
    class1.getsum();
    class2.getsum();
    class1.getsum_static();
    class2.getsum_static();
    return 0;
}
```

##### 静态成员变量

静态成员变量有以下特点:

1. 静态成员变量存储在全局数据区，由于静态数据需要在定义时分配空间，所以不能再类声明中定义，如上面的例子中使用`int Myclass::d=0;`对其进行定义
2. 由于静态成员变量存储在全局数据区，所以对于该类的多个对象来说，共享一个静态成员变量
3. 静态成员变量没有进入程序的全局名字空间，因此不存在与程序中其他全局名字冲突的可能性

##### 静态成员函数

静态成员函数有以下特点:

1. 对于该类的多个对象来说，共享一个静态成员函数(可以使用`<类名>::<静态成员函数名>`或`<对象名>.<静态成员函数名>`两种方式访问)，且**静态成员函数中没有`this`指针**
2. 静态成员函数只能访问静态数据成员和静态成员函数
3. 由于没有`this`指针的额外开销，因此静态成员函数与类的普通函数相比速度上有少许的增长