### chapter5 关联式容器set与map


#### 关联式容器set

`set`底层采用`RB-tree`实现，其键值就是实值，实值就是键值。

同时，我们不可以通过`set`的迭代器改变`set`的元素值，因为`set`元素值就是其键值，关系到`set`元素的排列规则。在`set`的源代码中，`set<T>::iterator`被定义为底层`RB-tree`的`const_iterator`,杜绝写入操作。

标准的`STL set`使用`RB-tree`作为底层机制，其所开放的各种操作接口都只是转调用`RB-tree`的操作行为。

`set`不允许两个元素有相同的键值，所以其`insert`操作调用的是底层`RB-tree`的`insert_unique()`操作。

相比于`set`,`multiset`运行两个元素有相同的键值，因此它的插入操作采用的是底层机制`RB-tree`的`insert_equal()`。

实现的部分`set`代码可以参考[github](https://github.com/lingqing97/tinySTL/blob/master/stl_wj_set.h)

#### 关联式容器map

`map`的底层机制同样是`RB-tree`,其所有元素都是`pair`，同时拥有实值(`value`)和键值(`key`),其中`pair`的第一元素被视为键值，第二元素被视为实值。同`set`一样，`map`也不允许两个元素拥有相同的键值。

`map`的部分定义如下:

```cpp
template<class Key,class T,class Compare=wj::less<Key>>
class map{
    public:
        //typedefs
        typedef Key key_type;   //键值类别
        typedef T data_type;    //数据类别
        typedef T mapped_type;
        typedef wj::pair<const Key,T> value_type;   //元素类型
        typedef Compare key_compare;    //键值比较函数

    //...

    private:
        typedef wj::rb_tree<key_type,value_type,wj::select1st<value_type>,key_compare> rep_type;
        rep_type t;     //以红黑树表现map
    public:

        //...

        //subscript operator
        T& operator[](const key_type& k){
            return (*(insert(value_type(k,T())).first)).second;
        }
        //insert
        wj::pair<iterator,bool> insert(const value_type& x){
            //返回pair
            return t.insert_unique(x);
        }
        //find
        iterator find(const key_type& x) { return t.find(x); }
};
```

从上述代码可以看出,`map`将`pair`声明为`value_type`。同时在`insert`操作中采用`RB-tree`的`insert_unique()`操作。

特别需要注意的是下标运算符，`map`的下标运算符是通过插入一个`value_type(k,T())`的临时元素来执行的，所以如果进行下标运算，输入的键值不存在,`map`会插入一个新元素,若键值存在，则会返回一个其实值(`value`)引用。

相比于`map`，`multimap`允许两个元素键值相同，所以其调用底层`RB-tree`的`insert_equal()`实现其插入操作。

部分`map`代码可以参考[github](https://github.com/lingqing97/tinySTL/blob/master/stl_wj_map.h)