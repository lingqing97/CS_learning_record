## Day-2

### 问题

> 实现string类的拷贝赋值成员

### 参考答案

参考:[让我们一步一步实现一个完整的 String 类：构造、拷贝、赋值、移动和析构](https://blog.csdn.net/u012814856/article/details/79753031)

```cpp
#include<iostream>
#include<cstring>

#define DEBUG

class String{
    private:
        char* m_data;
    public:
        String(const char* str=nullptr);
        String(const String&);
        String(String &&other):m_data(other.m_data) { other.m_data=nullptr;}
        String& operator=(const String&);
        String& operator=(String&&);
        ~String(){
            delete[] m_data;
        }
        #ifdef DEBUG
            void debug_print(){ printf("DEBUG: %s\n",m_data);}
        #endif
};

String::String(const char* str){                    //得分点1: 使用const才能接受const对象和非const对象
    //特别注意：空指针的时候要赋值一个空间
    if(str==nullptr){                               //得分点2: 对空指针自动申请一个空间存放结束标志'\0'
        m_data=new char[1];
        *m_data='\0';
    }
    else{
        m_data=new char[strlen(str)+1];             //得分点3: +1用于存储'\0'
        strcpy(m_data,str);
    }
}

String::String(const String& other){                //得分点4: 使用引用类型，规避递归使用拷贝构造的死循环问题(这里用于使用const,同得分点1)
    m_data=new char[strlen(other.m_data)+1];
    strcpy(m_data,other.m_data);
}

String& String::operator=(const String& other){
    #ifdef DEBUG
        printf("DEBUG: operator=(const String& other)\n");
    #endif
    //注意防止自赋值
    if(this==&other) return *this;                  //得分点5: 检测自赋值
    delete[] m_data;                                //得分点6: 释放原来的内存
    m_data=new char[strlen(other.m_data)+1];
    strcpy(m_data,other.m_data);
    return *this;
}

String& String::operator=(String&& other){
    #ifdef DEBUG
        printf("DEBUG: operator=(String&&)\n");
    #endif
    //注意防止自赋值
    if(this==&other) return *this;                  //得分点7：同得分点5
    m_data=other.m_data;                            //得分点8: 同得分点6
    other.m_data=nullptr;                           //得分点9：根据C++ primer中的建议，将使用后的右值置为空
    return *this;
}
```

```cpp
//测试
int main(void)
{
    //测试默认构造
    String mystr0;
    #ifdef DEBUG
        mystr0.debug_print();
    #endif
    //测试传参构造
    String mystr1("hello1");
    #ifdef DEBUG
        mystr1.debug_print();
    #endif
    //测试拷贝构造
    String mystr2(mystr1);
    #ifdef DEBUG
        mystr2.debug_print();
    #endif
    //测试移动构造
    String mystr3(std::move(mystr2));
    #ifdef DEBUG
        mystr3.debug_print();
    #endif
    //测试拷贝赋值
    mystr2=mystr1;
    #ifdef DEBUG
        mystr2.debug_print();
    #endif
    //测试移动赋值
    mystr2="hello2";
    #ifdef DEBUG
        mystr2.debug_print();
    #endif
    return 0;
}
```