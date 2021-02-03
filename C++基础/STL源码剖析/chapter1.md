### chapter1 STL 概论与版本简介


#### STL六大组件

STL提供六大组件，彼此可以组合套用:
1. 容器(`container`):如`vector`、`list`、`deque`用来存放数据。从实现的角度来看，STL容器是一种`class template`。
2. 算法(`algorithm`):如`sort`、`search`、`copy`等。从实现的角度来看,STL算法是一种`function template`。
3. 迭代器(`iterator`):是所谓的"泛型指针"，共有五种类型。所有STL容器都附带有自己专属的迭代器。
4. 仿函数(`functor`):行为类似函数，可作为算法的某种策略。从实现的角度来看，仿函数是一种重载了`operator()`的`class`或`class template`。
5. 配接器(`adapter`):一种用来修饰容器或仿函数或迭代器接口的东西
6. 配置器(`allocator`):负责空间配置与管理。从实现的角度来看，配置器是一个实现了动态空间配置、空间管理、空间释放的`class template`。

```cpp
//例子一：使用六大组件的简单例子
#include<vector>
#include<algorithm>
#include<functional>
#include<iostream>

using namespace std;

int main(){
    int ia[6]={27,210,12,47,109,83};
    vector<int,allocator<int>> vi(ia,ia+6);
//  ^^^^^      ^^^^^^^^^^^^^^
//  container  allocator
    cout<<count_if(vi.begin(),vi.end(),bind(less<int>(),_1,40));
//        ^^^^^^^             ^^^^^^^  ^^^^  ^^^^^^^^^^
//        algorithm           iterator adapter   functor
    return 0;
}
```

#### STL版本

* `HP`版本是所有STL实现版本的始祖
* `Visual C++`使用的由`P.J. Plauge`开发的`PJ STL`版本
* `C++ Builder`使用的由`Rouge Wave`公司开发的`RW STL`版本
* `GCC`使用的是有`Silicon Graphics Computer Systems,Inc`公司开发的`SGI`版本，其承继`HP`版本(《STL源码剖析》一书中以`SGI STL`作为讲解例子)