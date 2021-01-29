### 语句

#### 简单语句

* c++语言中的大多数语句都以分号结束，表达式语句的作用是执行表达式并丢弃掉求值结果

#### 语句作用域

* 定义在控制结构当中的变量只在相应语句的内部可见，一旦语句结束，变量也就超出其作用范围了

#### 条件语句

* 使用`if...else`要注意防范`悬垂else`
  * 就c++而言，它规定`else`与离它最近的尚未匹配的`if`匹配，从而消除了程序的二义性
* `case`关键字和它对应的值一起被称为`case标签`.`case标签`必须是`整型常量表达式`
* 如果`switch`结构以一个空的`default`标签作为结束，则该`default`标签后面必须跟上一条空语句或一个空块

```cpp
//例子一
char ch=getVal();
int ival=42;
switch(ch){
    case 3.14:          //错误：case标签不是一个整数
    case ival:          //错误：case标签不是一个常量
    //...
}

//例子二:把几个case标签写在一行里
switch(ch){
    case 'a': case 'e': case 'i': case 'o': case 'u':
        ++vowelCnt;
        break;
}

```

#### 迭代语句

* `while`和`for`语句在执行循环体之前检查条件，`do while`语句先执行循环体，然后再检查条件

#### 跳转语句

* `break`负责终止离它最近的`while`、`do while`、`for`或`switch`语句
  * `break`语句的作用范围仅限于最近的循环或者`switch`
* `continue`语句终止最近的循环中的当前迭代并立即开始下一次迭代
  * `continue`语句只能出现在`for`、`while`和`do while`循环的内部，或者嵌套在此类循环里的语句或块的内部
* `goto`语句的作用是从`goto`语句无条件跳转到同一函数内的另一条语句，尽量不要使用，因为它使得程序既难理解又难修改

#### try语句块和异常处理

* 在c++语言中，异常处理包括:
  * `throw表达式`:异常检测部分使用`throw`表达式来表示它遇到了无法处理的问题。我们说`throw`引发了(raise)异常
  * `try语句块`:异常处理部分使用`try`语句块处理异常。`try`语句块以关键字`try`开始，并以一个或多个`catch`子句结束
  * 一套`异常类`,用于在`throw`表达式和相关的`catch`子句之间传递异常的具体信息
* 当异常被抛出时，首先搜索抛出该异常的函数。如果没找到匹配的`catch`子句，终止该函数，并在调用该函数的函数中继续寻找
  * 如果最终还是没能找到任何匹配的`catch`子句，程序转到名为`terminate`的标准库函数,一般情况下，执行该函数将导致程序非正常退出

```cpp
//例子一：异常处理
try{
    program-statemetns
}catch(exception-declaration){
    handler-statements
}catch(exception-declaration){
    handler-statements
}
```