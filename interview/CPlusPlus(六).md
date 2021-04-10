## Day-6

### 问题

> 说一说C++中四种cast转换(即C++中的四种类型转换)

### 参考答案

参考:

1. [c++ 四种强制类型转换介绍](https://blog.csdn.net/ydar95/article/details/69822540)
2. [dynamic_cast彻底明白了~](https://blog.csdn.net/hongkangwl/article/details/21161713)
3. [C++类型转换之reinterpret_cast](https://zhuanlan.zhihu.com/p/33040213)


C++中有四种类型转换(建议看完上面3个参考资料，基本就掌握了):

1. const_cast: 去除对象的const属性
2. static_cast: C++隐式转换都基于此转换实现，可以用于常规类型的转换、基类和派生类之间的向上/向下转换（向下转换由于没有动态类型检查，所以不安全）
3. dynamic_cast: 提供更加安全的基类与派生类之间的转换, dynamic_cast用于向下转换时，之后基类指针运行时真正指向继承类指针才能转换成功
    * 对指针进行dynamic_cast，失败返回null，成功返回正常cast后的对象指针
    * 对引用进行dynamic_cast，失败抛出一个异常，成功返回正常cast后的对象引用
4. reinterpret_cast: 为运算对象在位模式上进行重新解释（具体可以查看参考资料3）

> PS： 要充分理解dynamic_cast和reinterpret_cast需要对C+的对象模型、内存模型有充分的认识（这也是面试的重点,需要注意!）

#### 例子

(理解这个例子基本足够了)

下面这个实例基本说明了四种类型转换的用法:

```cpp
#include<iostream>
using namespace std;

class Base
{
    //something
    public:
        // dynamic_cast只有在类有虚函数时才会进行类型检查，所以要使用dynamic_cast就需要定义虚函数
        virtual void print() { cout<<"I'm Base!"<<endl;}
};

class Sub: public Base
{
    //something
    public:
        virtual void print() { cout<<"I'm Sub!"<<endl;}
};

int main(void)
{
    /* const_cast用法:去除对象的const属性  */
    int a=10;
    const int* cp=&a;
    int* q=const_cast<int*>(cp);    //将指向常量的指针 转换为 指向普通变量的指针
    *q=20;
    cout<<*q<<endl;

    const int &cref_p=a;
    int &ref_p=const_cast<int&>(cref_p); //将常量引用 转换为 普通引用
    ref_p=30;
    cout<<ref_p<<endl;

    /* static_cast用法: C++ 中任何的隐式转换都是使用此转换实现 */

    // 常规类型的转换
    float fa=3.14;
    int ia=static_cast<int>(fa);
    cout<<ia<<endl;

    // 派生类到基类的向上转换
    // 编译通过，安全
    Sub sub;
    Base* base_ptr=static_cast<Base*>(&sub);

    // 基类到派生类的向下转换
    // 编译通过，不安全，没有动态类型检查
    Base base;
    Sub* sub_ptr=static_cast<Sub*>(&base);

    /* dynamic_cast用法：更加安全的基类与派生类之间的转换 */

    // 派生类到基类的向上转换
    // 此时和 static_cast 用法一样
    Sub sub2;
    Base* base_ptr2=dynamic_cast<Base*>(&sub2);
    if(base_ptr2!=NULL){
        base_ptr2->print();     //输出: I'm Sub!
    }


    // 基类到派生类的向下转换
    // 此时，只有基类指针运行是真正指向继承类才能转换成功
    Base base2;
    Sub* sub_ptr2=dynamic_cast<Sub*>(&base2);
    if(sub_ptr2!=NULL){     //此时转换失败 ,sub_ptr2是NULL
        sub_ptr2->print();
    }
    cout<<"sub ptr2:"<<sub_ptr2<<endl;  //输出: sub ptr2:0x0
    Base* base3=&sub2;
    Sub* sub_ptr3=dynamic_cast<Sub*>(base3);
    if(sub_ptr3!=NULL){
        sub_ptr3->print();              //输出: I'm Sub!
    }
    cout<<"sub ptr3:"<<sub_ptr3<<endl;  //输出: sub ptr3:0x7ffee2665438

    /* reinterpret_cast: 不会改变原本对象的值，而是从位模式上重新进行解释 */
    int num=0x00630061;
    int* pnum=&num;
    char* cnum=reinterpret_cast<char*>(pnum);
    /*
        输出:
            pnum指针的值0x7ffee188240c
            cnum指针的值0x7ffee188240c
            pnum指向的值630061
            cnum指向的值a
    */
    cout<<"pnum指针的值"<<pnum<<endl;
    cout<<"cnum指针的值"<<static_cast<void*>(cnum)<<endl;
    cout<<"pnum指向的值"<<hex<<*pnum<<endl;
    cout<<"cnum指向的值"<<*cnum<<endl;

    return 0;
}
```
