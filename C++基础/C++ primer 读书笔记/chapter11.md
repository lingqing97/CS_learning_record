### chapter11 关联容器

#### 11.1 使用关联容器

* 关联容器支持高效的关键字查找和访问，两个主要的关联容器类型是`map`和`set`
* 标准库提供8个关联容器，这8个容器的不同体现在三个维度上:
  * 是一个`set`,或是一个`map`
  * 要求不重复的关键字，或者允许重复关键字(允许重复关键字的容器名字汇总都有包含单词`multi`)
  * 按顺序保存元素，或无序保存(不保持关键字按照顺序存储的容器的名字都以单词`unordered`开头)

| 关联容器类型 | 特征 |
| :----: | :----: |
| map | 关联数组；保存关键字-值对 |
| set | 关联字即值，即只保存关键字的容器 |
| multimap | 关键字可重复出现的map |
| multiset | 关键字可重复出现的set |
| unordered_map | 用哈希函数组织的map |
| unordered_set | 用哈希函数组织的set |
| unordered_multimap | 哈希组织的map;关键字可以重复出现 |
| unordered_multiset | 哈希组织的set;关键字可以重复出现 |

#### 11.2 关联容器概述

* 对于有序容器`map`,`multimap`,`set`,`multiset`，关键字类型必须定义元素比较的方法(见例子一)

```cpp
//例子一
bool compareIsbn(const Sales_data &lhs,const Sales_data &rhs){
    return lhs.isbn()<rhs.isbn();
}
//bookstore中的元素以ISBN的顺序进行排列
multiset<Sales_data,decltype(compareIsbn)*> bookstore(compareIsbn);
```

#### 11.3 关联容器操作

| 类型别名 | 含义 |
| :----: | :----: |
| key_type | 此容器类型的关键字类型 |
| mapped_type | 每个关键字关联的类型；只适用于map |
| value_type | 对于set，与key_type相同；对于map,为`pair<const key_type,mapped_type>` |

* 当解引用一个关联容器的迭代器时，我们会得到一个`value_type`的值的引用(见例子一)
  * 对于`map`来说，`value_type`是`pair`类型，其`first`成员保存`const`的关键字
* <font color=red>当使用一个迭代器遍历一个`map`,`multimap`,`set`或`multiset`时，迭代器按关键字升序遍历元素</font>
* 对于不包含重复关键字的容器的`insert`操作和`emplace`操作，返回一个`pair`
  * `pair`的`first`成员是一个迭代器，指向具有给定关键字的元素
  * `pair`的`second`成员是一个`bool`值，指出元素是插入成功还是已经存在于容器中(见例子三)
* 对允许重复关键字的容器，接受单个元素的`insert`操作返回一个指向新元素的迭代器。
  * 这里无须返回一个`bool`值，因为`insert`总是向这类容器中加入一个新元素
* 关联容器定义了三个版本的`erase`(见例子四)
* 对一个`map`使用下标操作，其行为与数组或`vector`上的下标操作很不相同:
  * <font color=red>使用一个不在容器中的关键字作为下标，会添加一个具有此关键字的元素到`map`中</font>
* 如果一个`multimap`或`multiset`中有多个元素就有给定关键字，则这些元素在容器中会相邻存储，因为`multimap`和`multiset`都是有序的(见例子六)


```cpp
//例子一

//统计每个单词在输入中出现的次数
map<string,size_t> word_count;
string word;
while(cin>>word)
    ++word_count[word];
auto map_it=word_count.cbegin();
//*map_it是指向一个pair<const stirng,size_t>对象的引用
while(map_it!=word_count.cend()){
    cout<<map_it->first<<" occurs "
        <<map_it->second<<" tiems "<<endl;
    ++map_it;                       //递增迭代器，移动到下一个元素
}

//例子二:关联容器的insert操作
c.insert(v)                         //v是value_type类型的对象;args用来构造一个元素
c.emplace(args)

c.insert(b,e)                       //b和e是迭代器，表示一个c::value_type类型值的范围；
c.insert(il)                        //il是表示c::value_type类型值的花括号列表

//例子三
//统计每个单词在输入中出现次数的一种更繁琐的方法
map<string,size_t> word_count;      //从string到size_t的空map
string word;
while(cin>>word){
    //若word已在word_count中，insert什么也不做
    auto ret=word_count.insert({word,1});
    if(!ret.second)                 //word已在word_count中
        ++ret.first->second;        //递增计数器
}

//例子四：从关联容器删除元素
c.erase(k)                          //从c中删除每个关键字k的元素
                                    //返回一个size_type的值，指出删除的元素的数量

c.erase(p)                          //从c中删除迭代器p指定的元素
                                    //返回一个指向p之后元素的迭代器

c.erase(b,e)                        //删除迭代器对b和e所表示的范围中的元素
                                    //返回e

//例子五：在一个关联容器中查找元素的操作
c.find(k)                           //返回一个迭代器，指向第一个关键字为k的元素，若k不在容器中，则返回尾后迭代器
c.count(k)                          //返回关键字等于k的元素的数量，对于不允许重复关键字的容器，返回值永远是0或1

//例子六
string search_item("Alain de Botton");          //要查找的作者
auto entries=authors.count(search_item);        //元素的数量
auto iter=authors.find(search_item);            //此作者的第一本书
//用一个循环查找此作者的所有著作
while(entries){
    cout<<iter->second<<endl;
    ++iter;                                     //前进到下一本书
    --entries;                                  //记录已经打印了多少本书
}
```

> <font color=red>注意:</font>在map中查找元素是否存在，使用`find`,而不是使用下标操作

#### 11.4 无序容器

* 无序容器在存储上组织为一组桶，每个桶保存零个或多个元素