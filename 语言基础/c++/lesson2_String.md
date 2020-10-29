### 知识点1:三大函数（Big Three）:拷贝构造、拷贝复制、析构函数

#### 构造函数与析构函数
```c++
//构造函数
inline
String::String(const char* cstr=0){
    if(cstr){
        //+1用于存放结束符
        m_data=new char[strlen(cstr)+1];
        strcpy(m_data,cstr);
    }
    else{
        m_data=new char[1];
        *m_data='\0';
    }
}
//析构函数
inline
String::~String(){
    delete[] m_data;
}
```

#### 拷贝构造

* **class with pointer members必须有拷贝构造和拷贝赋值.**

```c++
//拷贝构造函数
inline
String::String(const String& str){
    m_data=new char[strlen(str.m_data)+1];
    strcpy(m_data,str.m_data);
}
// 拷贝构造函数的调用
// {
//        String s2(s1);
// }

//拷贝赋值函数
inline
Strnig& String::operator=(const String& str){
    //检测自我赋值
    if(this==&str)
        return *this;
    delete[] m_data;
    m_data=new char[strlen(str.m_data)+1];
    strcpy(m_data,str.m_data);
    return *this;w
}
//拷贝赋值函数的调用
//{
//      String s1=s2;
//}
```

### 知识点2:堆、栈与内存管理

```c++
class Complex{...};
...
{
    Complex c1(1,2); //存在于栈里面
    //heap是用户动态申请的内存空间
    Complex* p=new Complex(3);  //存在于heap里面
}
```

#### stack objects和static stack objects的生命期

```c++
class Complex{...};
...
{
    //auto object
    Complex c1(1,2)；   //析构函数自动调用
    //static object
    static Complex c2(1,2);//其生命在作用域结束之后仍然存在，直到整个程序结束
}
```

#### global objects的生命期

```c++
class Complex{...};
//global object
Complex c3(1,2);    //其生命在整个程序结束之后才结束,可视为static object,其作用域为整个程序
...
{
    ....
}
```

#### heap objects的生命期

```c++
class Complex{...};
...
{
    Complex* p=new Complex;
    ...
    //p的生命期在deleted之后结束
    //不delete会出现内存泄露
    delete p;
}
```

#### new:先分配memory,再调用ctor

```c++
Complex* pc=new Complex(1,2);
//new的执行过程
//1. void* mem=operator new(sizeof(Complex));  ==>分配内存
//2. pc=static_cast<Complex*>(mem);     ==>转型
//3. pc->Complex::Complex(1,2);     ==>构造函数
```

#### deleta:先调用析构函数,再释放memory

```c++
String* ps=new String("hello");
...
delete ps;
//delete的执行过程
//1. String::~String(ps);   ==》析构函数
//2. operator delete(ps);   ==》释放内存
```




