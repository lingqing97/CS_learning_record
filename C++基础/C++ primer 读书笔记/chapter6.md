### chapter6 函数

#### 函数基础

* 一个典型的函数定义包括以下部分:`返回类型`、`函数名称`、`由0个或多个形参组成的列表`以及`函数体`
* 函数的调用完成两项工作:
  * 一是用实参初始化函数对应的形参
  * 二是将控制权转移给被调用函数，此时`主调函数`的执行被暂时中断，`被调函数`开始执行
* `return`语句也完成两项工作:
  * 一是返回`return`语句中的值（如果有的话）
  * 二是将控制权从被调函数转移回主调函数
* `局部静态对象`在程序的执行路径第一次经过对象定义语句时初始化，并且直到程序终止才被销毁，在此期间即使对象所在的函数结束执行也不会对它有影响
* 如果局部静态变量没有显示的初始值，它将执行值初始化，内置类型的局部静态变量初始化为0
* 和其他名字一样，函数的名字也必须在使用之前声明
  * 函数的声明和函数的定义非常类似，唯一的区别是函数声明无需函数体，用一个分号替代即可
  * 因为函数的声明不包含函数体，所以就无需形参的名字
  * 函数只能定义一次，但可以声明多次
* 建议在头文件中声明变量和函数，在源文件中定义变量和函数
  * 定义函数的源文件应该把含有函数声明的头文件包含进来，编译器负责验证函数的定义和声明是否匹配

#### 参数传递

* 当形参是引用类型时，它对应的实参是被`引用传递`或者函数被`传引用调用`. 当实参的值被拷贝给形参时，形参和实参是两个相互独立的对象，这样的实参被`值传递`或者函数被`传值调用`
* 如果函数无需改变引用形参的值，最好将其声明为常量引用
* <font color=red>当用实参初始化形参时会忽略掉顶层const；同时，当形参有顶层const时，传给它常量对象或者非常量对象都是可以的</font>
* 因为数组会被转换为指针，所以当我们为函数传递一个数组时，实际上传递的是指向数组首元素的指针
* `int main(int argc,char *argv[])`：第一个形参`argc`表示数组中字符串的数量,第二个形参`argv`是一个数组，它的第一个元素指向程序的名字，接下来的元素依次传递命令行提供的实参，最后一个指针之后的元素值保证为0
  * 当使用`argv`中的实参时，一定要记得可选的实参从`argv[1]`开始；`argv[0]`保存程序的名字，而非用户输入
* 为了编写能处理不同数量实参的函数，c++11新标准提供了两种主要的方法:
  * 一是如果所有的实参类型相同，可以传递一个名为`initializer_list`的标准库类型(`initializer_list`提供的操作见例子四)
  * 二是如果实参的类型不同，可以编写一种特殊的函数，也就是所谓的可变参数模板，关于它的细节将在16章介绍
* `initializer_lsit`对象中的元素永远是常量值，我们无法改变其中的元素值
  * 在范围`for`循环中使用`initializer_list`对象时，应该使用`常量引用类型`

```cpp
//例子一：const形参和实参
//这种函数重载的形式是错误的，因为第二个fcn实际上与第一个没有区别
void fcn(const int i)
void fcn(int i)

//例子二：数组形参
//尽管形式不同，但这三个print参数是等价的
void print(const int*);
void print(const int[]);
void print(const int[10]);          //这里的维度表示我们期望数组含有多少元素，实际不一定

//例子三：管理指针形参的三种技术

//使用标记指定数组长度
void print(const char *cp){
    if(cp)
        while(*cp)  //处理c风格字符串遇到空字符停止
            cout<<*cp++;
}

//使用标准库规范
void print(const int *begin,const int *end){
    while(beg!=end)
        cout<<*beg++;
}

//显式传递一个表示数组大小的形参
void print(const int ia[],size_t size){
    //size表示数组的大小，将它显式地传递给函数用于控制对ia元素的访问
    for(size_t i=0;i!=size;++i)
        cout<<ia[i];
}

//例子四：initializer_list提供的操作
initializer_list<T> lst;            //默认初始化，T类型元素的空列表
initializer_lsit<T> lst{a,b,c...};  //lst的元素数量和初始值一样多
lst2(lst);                          //拷贝lst给lst2
lst2=lst;                           //拷贝lst给lst2
lst.size();                         //类别中的元素数量
lst.begin();                        //返回指向lst中首元素的指针
lst.end();                          //返回指向lst中尾元素下一位置的指针
```

#### 返回类型和return语句

* <font color=red>在含有`return`语句的循环后面应该也有一条`return`语句，如果没有的话该程序就是错误的，很多编译器都无法发现此类错误</font>
* 永远不要返回局部对象的引用或指针
* 调用一个返回引用的函数得到左值，其他返回类型得到右值
* `main`函数的返回值可以看做是状态指示器：返回0表示执行成功，返回其他值表示执行失败，其中非0值的具体含义依机器而定
  * `main`函数不能调用它自己
* 因为数组不能被拷贝，所以函数不能返回数组，不过函数可以返回数组的指针或引用(见例子一)

```cpp
//例子一：返回数组指针

//方式一
typedef int arrT[10];
using arrT=int[10];

arrT* func(int i);                  //func返回一个指向含有10个整数的数组的指针

//方式二
//Type (*function(parameter_list))[demension]     !!!!!! 声明一个返回数组指针的函数 !!!!!!!
int (*func(int i))[10];             //声明一个返回指向10个整数的数组的指针的函数

//方式三
auto func(int i) -> int(*) [10];            //使用尾置返回类型声明

//方式四
int odd[]={1,3,5,7,9};
int even[]={0,2,4,6,8};
//返回一个指针，该指针指向含有5个整数的数组
//decltype并不负责把数组类型转换成对应的指针，所以decltype的结果是个数组，所以在函数声明时还需加一个*fuhao
decltype(odd) *arrPtr(int i)
{
    return (i%2)?&odd;&even;
}
```

#### 函数重载

* 对于重载的函数来说，它们应该在形参数量或形参类型上有所不同
  * 不允许两个函数除了返回类型外其他所有的要素都相同
  * <font color=red>一个拥有顶层`const`的形参无法和另一个没有顶层`const`的形参区分开来</font>(见例子一)
  * 拥有底层`const`的形参可以和没有底层`const`的形参区分开来(见例子二)
* 如果我们在内层作用域中声明名字（包括变量，函数名等），它将隐藏外层作用域中声明的同名实体

```cpp
//例子一：顶层const形参无法区分
Record lookup(Phone);
Record lookup(const Phone);         //报错：无法重载

Record lookup(Phone*);
Record lookup(Phone *const);        //报错：无法重载

//例子二：底层const形参可以区分
Record lookup(Account&);
Record lookup(const Account&);        //正确：新函数

Record lookup(Account*);
Record lookup(const Account*);        //正确：新函数
```

#### 特殊用途语言特性

* 一旦某个形参被赋予了默认值，它后面的所有形参都必须有默认值
  * 当设计含有默认实参的函数时，其中一项任务就是合理设置形参的顺序，尽量让不怎么使用默认值的形参出现在前面，而让那些经常使用默认值的形参出现在后面
* 内联说明只是向编译器发出的一个请求，编译器可以选择忽略这个请求
* `assert`是一种预处理宏，定义在`cassert`头文件中，`assert(expr)`首先对`expr`求值，如果表达式为假，`assert`输出信息并终止程序的执行.如果表达式为真，`assert`什么也不做
* `assert`的行为依赖于一个名为`NDEBUG`的预处理变量的状态。如果定义了`NDEBUG`，则`assert`什么也不做。默认状态下没有定义`NDEBUG`,此时`assert`将执行运行时检查
  * 除了用于`assert`外，也可以使用`NDEBUG`编写自己的条件调试代码（见例子一）


```cpp
//例子一：使用NDEBUG编写条件调试代码
/*
除了c++定义几个对调试有用的名字:
    __func__:输出当前调试的函数的名字
    __FILE__:存放文件名的字符串字面值
    __LINE__:存放当前行号的整型字面值
    __TIME__:存放文件编译时间的字符串字面值
    __DATE__:存放文件编译日期的字符串字面值
*/

if(word.size()<threshold)
    cerr<<"Error:"<<__FILE__
        <<" : in function "<<__func__
        <<" at line "<<__LINE__
        <<" Compliled on "<<__DATE__
        <<" at "<<__TIME__<<endl
        <<" Word read was \""<<word
        <<"\":Length too shoart "<<endl;
```

#### 函数匹配

* 函数匹配有三步:`确定候选函数`->`从候选函数中确定可行函数`->`从可行函数中寻找最佳匹配`(如果有的话)
  * 候选函数具有两个特征：一是与被调用的函数同名，二是其声明在调用点可见
  * 可行函数也有两个特征：一是其形参数量与本次调用提供的实参数量相同，二是每个实参的类型与对应的形参类型吸纳共同，或者能转换成形参的类型
* 为了确定最佳匹配，编译器将实参类型到形参类型的转换划分成几个等级，具体排序如下所示(类类型转换等级最低)
    1. 精确匹配，包括以下情况:
        * 实参类型和形参类型相同
        * 实参从数组类型或函数类型转换成对应的指针类型
        * 向实参添加顶层`const`或从实参中删除顶层`const`
    2. 通过`const`转换实现的匹配
    3. 通过类型提升实现的匹配
    4. 通过算术类型转换或指针转换实现的匹配
    5. 通过类类型转换实现的匹配
* 如果有且只有一个函数满足下列条件（即“最匹配”），则匹配成功，否则编译器将报告二义性调用的信息:
  * 该函数每个实参的匹配都不劣于其他可行函数需要的匹配
  * 至少有一个实参的匹配优于其他可行函数提供的匹配

#### 函数指针

* 函数指针指向的是函数而非对象，函数指针指向某种特定类型，<font color=red>函数的类型由它的返回类型和形参类型共同决定，与函数名无关</font>(见例子一)
  * 使用函数指针作为形参时，可以使用函数指针或函数名(见例子二)
  * 函数类型和函数指针的声明需要特别注意(见例子三)
  * 当定义一个返回指向函数类型的指针的函数时，我们必须把返回类型写成指针形式，编译器不会自动地将函数返回类型当成对应的指针类型处理(见例子四)

```cpp
//例子一：函数指针
bool (*pf)(const string&,const string&);            //未初始化的函数指针

//例子二：函数指针作为形参
void useBigger(const string &s1,const string &s2,
                bool pf(const string&,const string&));
//等价的声明：显示地将形参定义成指向函数的指针
void useBigger(const string &s1,const string &s2,
                bool (*pf)(const string&,const string&));

//例子三

//Func是函数类型
typedef bool Func(const string&,const string&);
//FuncP是指向函数的指针
typedef bool(*FuncP)(cosnt string&,const string&);

//例子四：返回指向函数的指针
//和返回指向数组的指针的函数的声明一样，这里也有四种方式声明返回指向函数的指针的函数

//方式一
using F=int(int*,int);          //F是函数类型，不是指针
using PF=int(*)(int*,int);      //PF是指针类型

PF f1(int);                     //正确
F f1(int);                      //错误：F是函数类型,f1不能返回一个函数
F *f1(int);                     //正确：显示地指定返回类型是指向函数的指针

//方式二

int (*f1(int))(int*,int);


//方式三

auto f1(int) -> int(*)(int*,int);

//方式四
string::size_type sumLength(const string&,const string&);
decltype(sumLength) *getFcn(const string&);     //这里decltype得到的函数类型，所以需要显示地指定返回类型是指向函数的指针
```
