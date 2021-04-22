## Day-14

### 问题

> C++源文件从文本到可执行文件经历的过程?

### 参考答案

参考:

1. [一个C++源文件从文本到可执行文件经历的过程](https://blog.csdn.net/daaikuaichuan/article/details/89060957)
2. [C++源文件到可执行文件的过程](https://blog.csdn.net/sheng_ai/article/details/47860403)
3. [一个C++源文件从文本到可执行文件经历的过程](https://www.cnblogs.com/buerdepepeqi/p/12361355.html)

C++源文件到可执行文件分为四个阶段:`预处理`,`编译`,`汇编`和`链接`.

#### 预处理

预处理是对C++源文件进行编译前的预备处理，预处理后将得到一个`.i`后缀的预处理文件.

```cpp
//g++ 预处理指令
g++ -E helloworld.cpp -o helloworld.i
```

预处理主要完成以下工作:

1. 去除`#define`,并将宏定义展开
2. 处理预编译命令`#ifdef`,`#ifndef`等，去除不需要的代码
3. 处理`#include`预编译命令，递归地将文件插入到该预编译命令处
4. 去除所有`/**/`和`//`注释的内容
5. 添加行号和文件名标识
6. 保留`#pragma`编译器指令

```cpp
//helloworld.cpp

#include<iostream>
#define PRINT_OK

int main(void)
{
    //output
    #ifdef PRINT_OK
        std::cout<<"ok"<<std::endl;
    #else
        std::cout<<"hello world!"<<std::endl;
    #endif

    return 0;
}
```

对`helloworld.cpp`进行预处理后得到的`helloworld.i`文件用编辑器打开后如下:

```cpp
//helloworld.i

//这里只展示结尾的少部分代码
# 45 "/Library/Developer/CommandLineTools/usr/bin/../include/c++/v1/iostream" 3


namespace std { inline namespace __1 {


extern __attribute__ ((__visibility__("default"))) istream cin;
extern __attribute__ ((__visibility__("default"))) wistream wcin;


extern __attribute__ ((__visibility__("default"))) ostream cout;
extern __attribute__ ((__visibility__("default"))) wostream wcout;

extern __attribute__ ((__visibility__("default"))) ostream cerr;
extern __attribute__ ((__visibility__("default"))) wostream wcerr;
extern __attribute__ ((__visibility__("default"))) ostream clog;
extern __attribute__ ((__visibility__("default"))) wostream wclog;

} }
# 2 "helloworld.cpp" 2


int main(void)
{


        std::cout<<"ok"<<std::endl;




    return 0;
}
```

通过对比可以发现`helloworld.i`文件将头文件`iostream`中的代码包含了进来，导致文件代码非常多，同时可以发现宏定义、注释、预编译命令都被处理了。

> 追问:`#ifdef`、`#ifndef`等预编译命令的作用?`#include<>`和`#include""`的区别?`#pragma`的作用?

#### 编译

编译是将预处理文件经过`词法分析`,`语法分析`,`语义分析`以及`优化`后产生相应的`.s`后缀的汇编代码文件。（这一过程设计编译原理大量知识）

```cpp
g++ -S helloworld.i -o helloworld.s
```

可以用编辑器对汇编代码文件进行查看，部分汇编代码如下所示:

```
//helloworld.s

## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movq	%rdi, -8(%rbp)
	movl	%esi, -12(%rbp)
	movq	-8(%rbp), %rdi
	movl	32(%rdi), %esi
	orl	-12(%rbp), %esi
	callq	__ZNSt3__18ios_base5clearEj
	addq	$16, %rsp
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__cstring,cstring_literals
L_.str:                                 ## @.str
	.asciz	"ok"


.subsections_via_symbols
```

> 进阶：编译原理相关知识?

#### 汇编

`汇编`是将汇编语言代码翻译为机器指令的过程，生成`.o`后缀的目标文件.

```cpp
gcc -c helloworld.s -o helloworld.o
```

#### 链接

`链接`是将独立编译的源代码组装起来的过程，生成可执行文件。`链接`的过程包括`地址和空间的分配`、`符号决议`和`重定位`等步骤.

`链接`是将多个库组装在一起的过程，`链接库`分为`静态链接库`(**.a、.lib**)和`动态链接库`(**.so、.dll**)。windows上对应的是`.lib`和`.dll`,linux上对应的是`.a`和`.so`。

下面摘自[一个C++源文件从文本到可执行文件经历的过程](https://blog.csdn.net/daaikuaichuan/article/details/89060957)中的总结:

> 静态库可以简单看成是一组目标文件（.o/.obj文件）的集合，即很多目标文件经过压缩打包后形成的一个文件。静态库的缺点在于：浪费空间和资源，因为所有相关的目标文件与牵涉到的函数库被链接合成一个可执行文件。

> 动态库在程序编译时并不会被连接到目标代码中，而是在程序运行是才被载入。不同的应用程序如果调用相同的库，那么在内存里只需要有一份该共享库的实例，规避了空间浪费问题。