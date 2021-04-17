## Day-11

### 问题

> 请你说一下fork函数

### 参考答案

`fork`函数的作用是**在一个已经存在的进程中创建一个新进程，这个新进程称为子进程，原进程称为父进程。**

子进程是父进程的副本。由于我们知道程序=代码+数据，对于代码（正文段），父子进程是共享的，而对于数据（堆栈等），子进程是通过`写时拷贝`来保证数据的独立性(具体可以参考[Linux fork函数深度解析（写时拷贝+进程终止（exit）+进程等待（wait，waitpid））](https://blog.csdn.net/du1232/article/details/115360457))。

`fork`一般有两种用法:

1. 一个父进程希望复制自己，使父进程和子进程同时执行不同的代码
2. 一个进程要执行一个不同的程序，在这种情况下，子进行从`fork`返回后立刻调用`exec`

`fork`执行失败的原因主要有两个:

1. 系统中已经有太多的进程
2. 该实际用户ID的进程总数超过了系统限制

### 补充：fork与vfork的区别

`vfork`也用于创建一个新进程，而通过`vfork`创建新进程的目的是`exec`一个新程序。

`fork`与`vfork`的区别主要有两点:

1. `vfork`创建的子进程与父进程共享数据段，而`fork`创建的子进程与父进程不共享数据段
2. `vfork`保证子进程先运行，在它调用`exec`或`exit`之后父进程才可能被调用执行；而`fork`创建的子进程与父进程的执行不确定，由系统调度决定

参考:

1. [Linux fork函数深度解析（写时拷贝+进程终止（exit）+进程等待（wait，waitpid））](https://blog.csdn.net/du1232/article/details/115360457)
2. [深度解析Linux进程管理](https://blog.csdn.net/CZHLNN/article/details/114801517)
3. [fork与vfork的区别](https://blog.csdn.net/jianchi88/article/details/6985326)