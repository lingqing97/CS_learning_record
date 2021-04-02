## Day-4

### 问题

> 请说出const尽可能多的作用

### 参考答案

参考:

1. [C++ const的各种用法详解](https://www.cnblogs.com/wintergrass/archive/2011/04/15/2015020.html)
2. [const成员变量](https://www.cnblogs.com/kaituorensheng/p/3244910.html)
3. [C++中的const成员函数和const类对象](https://blog.csdn.net/v_xchen_v/article/details/65440554)

`const`在`C++`中的用法可以分为以下几类:

1. `const`修饰变量和数组

   * 常变量: `const + 类型 + 变量名`  / `类型 + const + 变量名`
   * 常数组: `const + 类型 + 数组名[大小]` / `类型 + const + 数组名[大小]`

2. `const`修饰指针以及引用

   * 常引用: `const + 类型 + &引用名` / `类型 + const + &引用名`
   * 指向常量的指针: `const + 类型 + *指针名` / `类型 + const + *指针名`(注意与常指针区分开来)
   * 常指针: `类型 + *const + 指针名`

3. `const`在类中的用法

   * 常数据成员: `const + 类型 + 数据成员名`  / `类型 + const + 数据成员名`
   * 常成员函数: `类型 + 类名:fun(形参) + const`

4. `const`修饰类对象

* 常对象: `const + 类名 + 对象名` / `类名 + const + 对象名`

#### 常变量和常数组

```cpp
const int a=10;             // 等价于 int const a=10;
const int arr[3]={1,2,3};   // 等价于 int const arr[3]={1,2,3};
```

在使用常变量和常数组时，只要不改变这些变量的值便好.

#### `const`修饰指针以及引用

```cpp
int e=1;
int *const const_ptr=&e;        //常指针
int const* cint_ptr=&e;         //指向常量的指针,等价于 const int* cint_ptr=&a;
const int &const_refer=e;      //常量引用,等价与int const& const_refer=e;
```

常指针表示不能对指针进行更改操作，但可以对其指向的元素进行更改操作;
指向常量的指针表示指针指向一个常量，不能对该指针指向的元素进行更改操作;
常量引用表示不能对引用的对象进行更改操作;

#### `const`在类中的用法

```cpp
class Myclass
{
    public:
        Myclass(int a=0):myA(a){
            // myA(a); 不可以在构造函数体内初始化
        }
        //const可以区分重载函数
        void print(){
            //print myA
        }
        void print() const{
            //print myA...
        }
    private:
        const int myA;
        static int const myB;
};

int const Myclass::myB=20;  //static const在类外初始化
```

对于`const`修饰的成员变量必须在构造函数初始化列表中初始化，<font color=red>而不可以在构造函数体内初始化</font>。

任何<font color="red">不修改</font>数据成员的函数都应该声明为`const`类型。如果在编写`const`成员函数时，不慎修改了数据成员，或<font color="red">调用了其他非`const`成员函数</font>，编译器就会指出错误.


#### `const`修饰类对象

```cpp
class Myclass
{
    public:
        Myclass(int a=0):myA(a){}
        void print(){
            std::cout<<myA<<std::endl;
        }
        void print() const{
            std::cout<<"use print()"<<std::endl;
        }
    private:
        const int myA;
        static int const myB;
};
int main(void)
{
    Myclass c1;
    c1.print();         //输出0
    const Myclass c2;
    c2.print();         //输出use print
    return 0;
}
```

非const类对象既可以访问const成员函数也可以访问非const成员函数，const类对象只能访问const成员函数。