### chapter6 算法

#### STL算法概述


所有泛型算法的前两个参数都是一对迭代器，通常称为`first`和`last`，用以标示算法的操作区间，该区间是一个前闭后开区间，即`[first,last)`。

由前面章节我们知道，STL中迭代器可以分为5类，在每一个STL算法的声明中，都表现出它所需要的最低程度的迭代器类型。

所有数值算法，包括`adjacent_difference()`,`accumulate()`,`inner_product()`,`partial_sum()`等等，都实现于`stl_numeric.h`文件中，这是个内部文件，STL规定用户必须包含上层的`<numeric>`。其他`STL`算法都实现于SGI的`stl_algo.h`和`stl_algobase.h`文件中，也都是内部文件，欲使用这些算法，必须先包含上层相关头文件`<algorithm>`。


#### 数值算法概述

STL的数值算法实现在内部文件`stl_numeric.h`中。常见的数值算法有`accumulate()`,`power()`等，实现如下:

```cpp
//accumulate
template<class InputIterator,class T>
T accumulate(InputIterator first, InputIterator last, T init){
    for(;first!=last;++first)
        init=init+ *first;
    return init;
}

template<class InputIterator,class T,class BinaryOperation>
T accumulate(InputIterator first,InputIterator last,T init,BinaryOperation op){
    for(;first!=last;++first)
        init=op(init,*first);
    return init;
}

//power
template<class T,class Interger,class MonoidOperation>
T power(T x, Interger n, MonoidOperation op){       //快速幂算法
    if(n==0)
        return wj::identity(op);
    else{
        while((n&1)==0){
            n>>=1;
            x=op(x,x);
        }
        T result=x;
        n>>=1;
        while(n!=0){
            x=op(x,x);
            if((n&1)!=0)
                result=op(result,x);
            n>>=1;
        }
        return result;
    }
}
```

#### algobase.h中的算法

SGI将一些常用的算法定义在`stl_algobase.h`文件中，其他较复杂和不常用的算法定义于`stl_algo.h`中。典型的算法有逻辑比较函数`lexicographical_compare()`,`min()`,`max()`,`swap()`等函数,部分实现如下:

```cpp
//lexicographic_compare
 template<class InputIterator1,class InputIterator2>
 bool lexicographic_compare(InputIterator1 first1,InputIterator1 last1,
                     InputIterator2 first2,InputIterator2 last2)
 {
     for(;first1 != last1 && first2!=last2; ++first1,++first2){
         if(*first1<*first2){
             return true;
         }
         if(*first1>*first2){
             return false;
         }
     }
     return first1==last1&&first2!=last2;
 }

 template<class InputIterator1,class InputIterator2,class Compare>
 bool lexicographic_compare(InputIterator1 first1,InputIterator1 last1,
                     InputIterator2 first2,InputIterator2 last2,Compare comp)
 {
     for(;first1 != last1 && first2!=last2; ++first1,++first2){
         if(comp(*first1,*first2)){
             return true;
         }
         if(comp(*first2,*first1)){
             return false;
         }
     }
     return first1==last1&&first2!=last2;
 }

 //swap
 template<class T>
 inline void swap(T& a,T& b){
     T tmp=a;
     a=b;
     b=tmp;
 }
```

#### 其他算法

STL提供了四种与set（集合）相关的算法，分别是并集`set_union()`,交集`set_intersection()`,差集`set_difference()`和对称差集`set_symmetric_difference()`。这四个算法只能用于有序的`set`,而不能用于无序的`set`，即`hash_set/hash_multiset`不能使用这四个算法。四个算法实现如下:

```cpp
//实现set相关算法
//求两个set并集
template<class InputIterator1,class InputIterator2,class OutputIterator>
OutputIterator set_union(InputIterator1 first1,InputIterator1 last1,
                            InputIterator2 first2,InputIterator2 last2,
                            OutputIterator result)
{
    while(first1!=last1&&first2!=last2){
        if(*first1<*first2){
            *result=*first1;
            ++first1;
        }
        else if(*first2<*first1){
            *result=*first2;
            ++first2;
        }
        else{
            *result=*first1;
            ++first1;
            ++first2;
        }
        ++result;
    }
    //将尚未到达尾端的区间的所有剩余元素拷贝到目的端
    //此时[first2,last2)和[first1,last1)一定有一个是空的
    return std::copy(first2,last2,std::copy(first1,last1,result));
}

//求两个set交集
template<class InputIterator1,class InputIterator2,class OutputIterator>
OutputIterator set_intersection(InputIterator1 first1,InputIterator1 last1,
                                InputIterator2 first2,InputIterator2 last2,
                                OutputIterator result)
{
    while(first1!=last1&&first2!=last2){
        if(*first1<*first2){
            ++first1;
        }
        else if(*first2<*first1){
            ++first2;
        }
        else{
            *result=*first1;
            ++result;
            ++first1;
            ++first2;
        }
    }
    return result;
}

//求两个set差集
template<class InputIterator1,class InputIterator2,class OutputIterator>
OutputIterator set_difference(InputIterator1 first1,InputIterator1 last1,
                                InputIterator2 first2,InputIterator2 last2,
                                OutputIterator result)
{
    while(first1!=last1&&first2!=last2){
        if(*first1<*first2){
            *result=*first1;
            ++result;
            ++first1;
        }
        else if(*first2<*first1){
            ++first2;
        }
        else{
            ++first1;
            ++first2;
        }
    }
    return std::copy(first1,last1,result);
}

//求两个set对称差
template<class InputIterator1,class InputIterator2,class OutputIterator>
OutputIterator set_symmetric_difference(InputIterator1 first1,InputIterator1 last1,
                                InputIterator2 first2,InputIterator2 last2,
                                OutputIterator result)
{
    while(first1!=last1&&first2!=last2){
        if(*first1<*first2){
            *result=*first1;
            ++result;
            ++first1;
        }
        else if(*first2<*first1){
            *result=*first2;
            ++result;
            ++first2;
        }
        else{
            ++first1;
            ++first2;
        }
    }
    return std::copy(first2,last2,std::copy(first1,last1,result));
}
```

STL还提供了`lower_bound`和`upper_bound`两个常用的二分查找函数。**这个两个函数都应用于有序区间**，其中`lower_bound`会返回一个迭代器，指向第一个“不小于value”的元素（换种角度理解，即其返回值是"在不破坏排序状态的原则下，可插入value的第一个位置"）,而`upper_bound`则返回"在不破坏顺序的情况下，可插入value的最后一个合适位置"。

此外，STL还提供了`sort()`算法。这个算法仅接受两个`RandomAccessIterators`，所以未提供该类迭代器的容器无法使用该算法（比如`list`和`slist`,但它们都提供了自定义的排序函数）。

STL的sort算法是一种混合式排序算法:`Introspective Sorting(内省式排序)`，简称`IntroSort`：数据量大时采用快速排序，一旦分段后的数据量小于某个阈值，为避免快速排序的递归调用带来过大的额外复旦，就改用插入排序`Insertino Sort`.如果递归层次过深，还会改用堆排序`Heap Sort`。


