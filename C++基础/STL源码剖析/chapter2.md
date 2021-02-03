### chapter2 空间配置器

#### 空间配置器的标准接口

为了精密分工，`STL allocator`将对象构造/析构,内存分配/释放分开来。内存分配操作由`allocator::allocate()`负责，内存释放操作由`alloc::deallocate()`负责；对象构造操作由`allocator::construct()`负责,对象析构操作由`allocator::destory()`负责。

根据`STL`的规范，以下是`allocator`的必要接口:

```cpp
//一组typedef
allocator::value_type
allocator::pointer
allocator::const_pointer
allocator::reference
allocator::const_reference
allocator::size_type
allocator::difference_type
//一个内嵌模板
allocator::rebind:allocator的内嵌模板，需要定义other成员
//一组成员函数
allocator::alocator():构造函数
allocator::alocator(const allocator&):拷贝构造函数
template<typename T> allocator::allocator(const allocator<T>&):泛化的拷贝构造函数
allocator::~allocator():析构函数
pointer allocator::address(reference x) const:返回对象地址,相当于&x
pointer allocator::allocate(size_type n,const void*=0):分配可以容纳n个对象的空间，对象类别是T
void allocator::deallocator(pointer p,size_type n):释放空间
size_type allocator::max_size() const:可以分配的最大空间
void allocator::construct(pointer p,const T& x):相当于new(const void*)p) T(x)
void allocator::destory(pointer p):相当于p->~T()
```

在满足上述标准接口的基础上，我们可以实现一个简单的自定义内存分配器

```cpp
//简单的自定义内存分配器
#ifndef _WJALLOC_
#define _WJALLOC_

#include<new>               //for placement new
#include<cstddef>           //for ptrdiff_t,size_t
#include<cstdlib>           //for exit(),malloc()
#include<climits>           //for UNIT_MAX
#include<iostream>          //for cerr

namespace wj{
    template<typename T>
    class allocator{
        public:
            //一组typedef
            typedef T               value_type;
            typedef T*              pointer;
            typedef const T*        const_pointer;
            typedef T&              reference;
            typedef const T&        const_reference;
            typedef size_t          size_type;
            typedef ptrdiff_t       difference_type;

            //定义内置的模板版本
            template<typename U>
            struct rebind {
                typedef allocator<U> other;
            };

            //allocate和deallocate
            pointer allocate(size_type n,const void* p=0){
                pointer buffer=(T*) malloc(n*sizeof(T));
                //内存不足这里不进行处理
                if(buffer==0){
                    std::cerr<<"out of memory"<<std::endl;
                    exit(1);
                }
                return buffer;
            }
            void deallocate(pointer p,size_type n){
                if(p!=nullptr){
                    free(p);
                }
            }
            //construct和destory
            void construct(pointer p,const T& value){
                new(p) T(value);            //使用placement new,在地址p出构造T,并将value值传给T
            }
            void destory(pointer p,size_type n){
                p->~T();                    //调用T的析构函数销毁之
            }
            //mas_size
            size_type max_size() const{
                return size_type(UINT_MAX/sizeof(T));
            }
            //address和const_address
            pointer address(reference x){
                return (pointer)(&x);
            }
            const_pointer const_address(const_reference x){
                return (const_address)(&x);
            }
    };
}

#endif
```

使用`std::vector`搭配自定义的内存分配器进行测试

```cpp
#include"stl_wjalloc.h"
#include<vector>
#include<iostream>
using std::vector;

int main(){
    int elements[]={1,2,4,5,6,3,2,4};
    const int n=sizeof(elements)/sizeof(int);
    vector<int,wj::allocator<int>> vec(elements,elements+n);
    //输出1 2 4 5 6 3 2 4
    for_each(vec.begin(),vec.end(),[](int a){ std::cout<<a<<" "; });
    return 0;
}
```

#### SGI STL中的内存分配器

简易版的内存分配器还存在很多的不足，在`SGI STL`中设计了一个更加完美的内存分配器，其设计哲学如下:

1. 向`system heap`要求空间
2. 考虑多线程(`multi-threads`)状态
3. 考虑内存不足时的应变措施
4. 考虑过多"小型区块"可能造成的内存碎片(`fragment`)问题
为了控制问题的复杂度，《STL源码剖析》中未讨论多线程状态的处理。

##### 考虑内存不足时的应变措施

为了处理内存的不足，`SGI STL`中内存分配器借鉴了所谓的`C++ new handler`机制：`C++ new handler`机制可以要求系统在内存配置需求无法被满足时，调用一个你所指定的函数。

`C++ new handle`通过`set_new_handler`实现，定义在`std`中,在发生"OOM"时，会调用`set_new_handler`设定的`new_handler`处理函数进行处理,`new_handler`需要能申请到足够大的内存。(参考[理解C++ new-handler机制](https://blog.csdn.net/qilimi1053620912/article/details/89361479))

```cpp
namespace std{
    typedef void (*new_handler)();
    new_handler set_new_handler(new_handler new_p) throw;
    new_handler set_new_handler(new_handler new_p) noexcept();
}
```

可以像下面这样使用`new handler`:

```cpp
#include <iostream>
#include <new>

void handler()
{
    std::cout << "Memory allocation failed, terminating\n";
    std::set_new_handler(nullptr);
}

int main()
{
    std::set_new_handler(handler);
    try {
        while (true) {
            new int[100000000ul];
        }
    } catch (const std::bad_alloc& e) {
        std::cout << e.what() << '\n';
    }
}

//ouput:
//Memory allocation failed, terminating
//std::bad_alloc
```

由于内存分配器中实际使用的是`malloc`而非`::operator new`来配置内存，所以不能直接使用`C++`的`set_new_hanlder()`,必须仿真一个类似的`set_malloc_handler()`。其实现部分如下(以下是根据我自己的理解简化的代码，具体代码可以参考书p57部分):

```cpp
void (* __malloc_alloc_oom_handler)()=nullptr;            //将__malloc_alloc_oom_handler指向nullptr
//仿真C++ 的set_new_handler()
void (*set_malloc_handler(void (*f)()))()                 //返回一个函数指针void(*)(),传入void(*f)()
{
    void (*old)=__malloc_alloc_oom_handler;
    __malloc_alloc_oom_handler=f;
    return old;
}
```

在发生内存不足时，不断尝试调用`new_handler`处理函数，然后尝试再次配置内存，再尝试，在配置...,其处理内存不足的函数实现部分大概如下(以下代码是根据我自己的理解简化的代码，具体代码可以参考书p58部分):

```cpp
void* oom_malloc(size_t n)                              //在发生内存不足时调用该函数
{
    void (* my_malloc_handler)();                       //定义一个函数指针
    void *result;
    for(;;){                                            //不断尝试释放，配置，再释放，再配置...
        my_malloc_handler=__malloc_alloc_oom_handler;
        if(nullptr==my_malloc_handler){
            //未配置new handler函数，直接抛出异常
            throw bad_alloc();
        }
        (*my_malloc_handler)();                         //调用new handler尝试获得更多内存
        result=malloc(n);                               //再次尝试配置内存
        if(result) return result;
    }
}
```

##### 考虑过多"小型区块"可能造成的内存碎片(`fragment`)问题

当使用`malloc`给小型区块分配内存时可能会产生`外碎片`(参考[malloc原理和内存碎片](https://blog.csdn.net/xiaofei0859/article/details/72783391))

`malloc`会根据区块的大小来选择不同的内存分配方式:
* 当`malloc`小于`128k`时，使用`brk`将`数据段(.data)的最高地址指针_edata往高地址推`
* 当`malloc`大于`128k`时，使用`mmap在堆和栈之间找一块空闲内存分配`

`free()`可以直接回收`mmap`分配的内存，而`brk`分配的内存则要一定条件(`free()`释放的空闲内存大于`128k`)才回收,这就会导致低地址的内存被`free()`之后仍然无法使用，从而产生`外碎片`.

除了`外碎片`,分配小型区块还可能产生`内碎片`,比如对于32位的机器，如果要求`3字节`的内存，实际分配的是`4字节`,有`1字节`是系统用于对齐用的，这部分也就是`内碎片`。

`SGI STL`中采用`内存池(memory pool)`对分配的内存进行统一管理：每次都向系统申请一大块内存，并维护对应的自由链表。（相关内容见《STL源码剖析》p69）

#### 最后

根据`SGI STL`中处理内存不足的方法，我自己改进了简化版的内存分配器，其实现在[github](https://github.com/lingqing97/tinySTL/blob/master/stl_wjalloc.h)中