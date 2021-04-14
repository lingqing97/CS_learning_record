## Day-9

### 问题

> 请你实现c++中的shared_ptr

### 参考答案

参考:[面试题：简单实现一个shared_ptr智能指针](https://cloud.tencent.com/developer/article/1688444)

`shared_ptr`的核心是通过一个引用计数来统计指向对象的指针数量，当该引用计数为0时则释放对象资源。

```cpp
#include<iostream>
#include<mutex>
using namespace std;

template<typename T>
class my_shared_ptr{
    private:
        int* _pRef;
        T* _pPtr;
        mutex* _pMutex;
    private:
        void release()
        {
            bool isRelease=false;
            //加锁：保证对引用计数的线程安全
            _pMutex->lock();
            if(--(*_pRef)==0)
            {
                delete _pPtr;
                delete _pRef;
                _pPtr=nullptr;
                _pRef=nullptr;
                isRelease=true;
            }
            _pMutex->unlock();
            if(isRelease){
                delete _pMutex;
                _pMutex=nullptr;
            }
        }
        void addRef(){
            _pMutex->lock();
            ++(*_pRef);
            _pMutex->unlock();
        }
    public:
        my_shared_ptr(T* ptr=nullptr):_pRef(new int(1)),_pPtr(ptr),_pMutex(new mutex){}
        ~my_shared_ptr(){ release(); }
        my_shared_ptr(const my_shared_ptr& rhs):_pRef(rhs._pRef),_pMutex(rhs._pMutex),_pPtr(rhs._pPtr){
            addRef();
        }
        my_shared_ptr& operator=(my_shared_ptr& rhs){
            if(_pPtr!=rhs._pPtr){
                //释放管理的旧内容
                release();
                _pRef=rhs._pRef;
                _pPtr=rhs._pPtr;
                _pMutex=rhs._pMutex;
                addRef();
            }
            return *this;
        }
        T& operator*(){ return *_pPtr; }
        T* operator->() { return _pPtr; }
        int use_count() const { return *_pRef; }
};

//Test
int main(void)
{
    my_shared_ptr<int> p1(new int(1));
    cout<<*p1<<endl;
    {
        my_shared_ptr<int> p2=p1;
        cout<<*p2<<endl;
        cout<<"use count "<<p2.use_count()<<endl;
    }
    cout<<"use count "<<p1.use_count()<<endl;
    {
        my_shared_ptr<int> p3(p1);
        cout<<*p3<<endl;
        cout<<"use count "<<p3.use_count()<<endl;
    }
    cout<<"use count "<<p1.use_count()<<endl;
    return 0;
}
/*
输出
1
1
use count 2
use count 1
1
use count 2
use count 1
*/
```

#### 线程安全

关于线程安全，这里直接摘取参考资料[面试题：简单实现一个shared_ptr智能指针](https://cloud.tencent.com/developer/article/1688444)中的原文：

> 智能指针对象中引用计数是多个智能指针对象共享的，两个线程中智能指针的引用计数同时++或– -，这个操作不是原子的，引用计数原来是1，++了两次，可能还是2.这样引用计数就错乱了。会导致资源未释放或者程序崩溃的问题。所以智能指针中引用计数++、– -是需要加锁的，也就是说**引用计数的操作是线程安全的**

> 智能指针管理的对象存放在堆上，两个线程中同时去访问，会导致线程安全问题,也就是说**对智能指针共同指向的对象的操作不是线程安全的**

#### 循环引用

`shared_ptr`的循环引用会导致死锁，从而使得资源不能被释放，通过`weak_ptr`可以解决这个问题，具体参考:[[每天一道面试题 c++] Day8 讲讲你理解的c++四大智能指针](https://blog.csdn.net/qq_39621037/article/details/115658557)