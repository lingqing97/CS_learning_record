[toc]

### chapter10 信号

#### 信号概念

`信号`是软件中断，在头文件`<signal.h>`中，信号名都被定义为正整数常量。不存在编号为`0`的信号。

> POSIX.1 将信号编号0定义为一个空信号，使用指令`kill(pid,0)`可以用来确定一个特定进程是否仍然存在，如果向一个并不存在的进程发送空信号，则`kill`返回`-1`.

当造成信号的事件发生时，向一个进程发送一个信号。这里的`事件`可以是硬件异常(如除以0)、软件条件(如alarm定时器超时)、终端产生的信号或调用`kill`函数.

在一个信号出现时，可以告诉内核按下列3种方式之一进行处理:

1. 忽略此信号，但有两种信号决不能被忽略，它们是`SIGKILL`和`SIGSTOP`，这两种信号不能被忽略的原因是：它们向内核和超级用户提供了使进程终止或停止的可靠方法
2. 捕捉信号，这是需要编写一个对应的信号处理函数
3. 执行系统默认动作，注意，对大多数信号，系统的默认动作是终止该进程

#### 函数signal

UNIX系统信号机制最简单的接口是`signal`函数

```cpp
#include<signal.h>

void (*signal(int signo,void (*func)(int)))(int);
```

上面所示的`signal`函数原型也可以写成:

```cpp
typedef void Sigfunc(int);

Sigfunc *signal(int,Sigfunc*);      //返回值：若成功，返回以前的信号处理配置；若出错，返回SIG_ERR
```

`signo`参数表示信号量，`func`可以取以下三种值:

1. `SIG_IGN`:向内核表示忽略此信号(记住有两个信号`SIGKILL`和`SIGSTOP`不能忽略)
2. `SIG_DFL`:表示接到此信号后的动作是系统默认动作
3. 指定函数地址：则在信号发生时，调用此函数，我们称这种处理为捕捉该信号，称此函数为`信号处理程序(signal handler)`或`信号捕捉函数(signal-catching function)`.

这里有两点需要注意:

1. 调用`exec`:`exec`函数将原先设置为要捕捉的信号都更改为默认动作，因为信号捕捉函数的地址很可能在所执行的新程序文件中已无意义了
2. 调用`fork`:当一个进程调用`fork`时，其子进程继承父进程的信号处理方式，因为子进程在开始时复制了父进程内存映像，所以信号捕捉函数的地址在子进程中石油意义的

##### 实例：捕捉SIGUSR1和SIGUSR2的简单程序

`SIGUSR1`和`SIGUSR2`是UNIX系统预留给用户的两个未定义信号

```cpp
#include<stdio.h>
#include<unistd.h>
#include<signal.h>

#define oops(m,x) { perror(m); exit(x); }

static void sig_usr(int);

/*
执行:
kill -USR1 1158
kill -USR2 1158
kill 1158       ---> kill指令默认发送SIGTERM信号
*/

int main(void)
{
    if(signal(SIGUSR1,sig_usr)==SIG_ERR)
        oops("signal error",1);
    if(signal(SIGUSR2,sig_usr)==SIG_ERR)
        oops("signal error",1);
    for(;;) pause();
    return 0;
}

static void sig_usr(int signo)
{
    if(signo==SIGUSR1)
        printf("receive SIGUSR1.\n");
    else if(signo==SIGUSR2)
        printf("receive SIGUSR2.\n");
    else
        printf("receive signal.\n");
}
```

#### 不可靠信号

在早期的UNIX版本中，信号是不可靠的，不可靠在这里指的是，信号可能会丢失：一个信号发生了，但进程却可能一直不知道这一点。

**早期版本中的一个问题是在进程每次接到信号对其进行处理时，随即将该信号动作重置为默认值。**

典型的例子是：在早期的UNIX系统中，如果进程在执行一个**低速系统调用**而阻塞期间捕捉到一个信号，则该系统调用就被中断不再继续执行。

其中，系统调用可以分为两类：`低速系统调用`和`其他系统调用`;低速系统调用时可能会使进程永远阻塞的一类系统调用。

为了使被中断的系统调用恢复，典型的代码程序如下:

```cpp
if((n=read(fd,buf,BUFSUZE))<0){
    if(errno==EINTR)    /* 阻塞期间捕捉到信号会中断系统调用，同时将errno置为EINTR */
        goto again;     /* 将由于这种情况而中断的系统调用恢复 */
}
```

为了帮助应用程序使其不必处理被中断的系统调用，4.2BSD引进了某些被中断系统调用的`自动重启动`。自动重启动的系统调用包括:`ioctl`、`read`、`readv`、`write`、`writev`、`wait`和`waitpid`.如前所述，**其中前5个函数只有对低速设备进场操作时才会被信号中断。而`wati`和`waitpid`在捕捉到信号时总是被中断**。

#### 可重入函数

`Single UNIX Specification`说明了在信号处理程序中保证调用安全的函数(如下图)，这些函数是`可重入`的并被称为是`异步信号安全的`.

![avatar](../images/../../image/unix_可重入函数.jpg)

以下函数通常是不可重入的:

1. 已知它们使用静态数据结构
2. 它们调用`malloc`或`free`
3. 它们是标准I/O函数，标准I/O库的很多实现都以不可重入方式使用全局数据结构

> 需要注意的是，即使信号处理程序调用的是可重入的函数，由于每个线程都有一个`errno`变量，所以信号处理程序可能会修改其原先值。因此，作为一个通用的规则，在信号处理程序中调用可重用函数时，应当在调用前保存`errno`，在调用后恢复`errno`.

#### 可靠信号术语和语义

在信号产生和传递之间的时间间隔内，称信号是`未决的(pending)`.

进程可以选用"阻塞信号递送"。如果为进程产生了一个阻塞的信号，而且对该信号的动作是系统默认动作或捕捉该信号，则为该进程将此信号保持未`未决状态`,直到进程对此信号解除了阻塞，或者将对此信号的动作更改为忽略。（每个进程都有一个信号屏蔽字，它规定了当前要阻塞递送到该进程的信号集）

需要注意的是，大多数系统对递送了多次的信号只递送一次。（在会对信号排队的系统中，信号会被递送多次）

#### 函数kill和raise

`kill`函数将信号发送给进程或进程组，`raise`函数则允许进程向自身发送信号：

```cpp
#include<signal.h>

//两个函数返回值：若成功，返回0；若出错，返回-1
int kill(pid_t pid,int signo);
int raise(int signo);      // <==>  等价于 kill(getpid(),signo);
```

#### 函数alarm和pause

使用`alarm`函数可以设置一个定时器(闹钟时间)，在将来的某个时刻该定时器会超时。当定时器超时时，产生`SIGALRM`信号。如果忽略或不捕捉此信号，则此默认动作是终止调用该`alarm`函数的进程.

```cpp
#include<unistd.h>

//返回值：0或以前设置的闹钟时间的余留秒数
unsigned int alarm(unsigned int seconds);
```

`重置闹钟`:每个进程只能有一个闹钟时间，如果在调用`alarm`时，之前已为该进程注册的闹钟时间还没有超时，则该闹钟时间的余留值作为本次`alarm`函数调用的值返回。以前注册的闹钟时间则被新值替代.
`关闭闹钟`:如果有以前注册的尚未超过的闹钟时间，而且本次调用的`seconds`值是0,则取消以前的闹钟时间，其余留值仍作为`alarm`函数的返回值.

`pause`函数使调用进程挂起直至捕捉到一个信号

```cpp
#include<unistd.h>

//返回值：-1,errno设置为EINTR
int pause(void);
```

只有执行了一个信号处理程序并从其返回时，`pause`才返回.

#### 信号集、函数sigprocmask和函数sigpending

我们用`信号集`(Unix中用数据结构`sigset_t`来表示)来表示多个信号，如下所示定义了5个处理信号集的函数.

```cpp
#include<signal.h>

//4个函数返回值：若成功，返回0；若出错，返回-1
int sigemptyset(sigset_t* set);                     //清空所有信号
int sigfillset(sigset_t* set);                      //包含所有信号
int sigaddset(sigset_t* set,int signo);             //加入某个信号
int sigdelset(sigset_t* set,int signo);             //删除某个信号

//返回值：若真，返回1；若假，返回0
int sigismember(const sigset_t* set,int signo);     //测试一个信号位是否设置
```

一个进程的`信号屏蔽字`规定了当前阻塞而不能递送到该进程的信号集。调用函数`sigprocmask`可以检测或更改，或同时进行检测和更改进程的信号屏蔽字。

```cpp
#include<signal.h>

//set是要设置的信号屏蔽字,oset是之前的信号屏蔽字,how指明了以何种方式设置信号屏蔽字
int sigprocmask(int how,const sigset_t *restrict set,sigset_t* restrict oset);
```

> 注意,`sigprocmask`是仅为单线程进程定义的，处理多线程进程中信号的屏蔽使用另一个函数。

##### 实例：为进程打印信号屏蔽字

```cpp
#include<stdio.h>
#include<unistd.h>
#include<signal.h>
#include<errno.h>

void pr_mask(const char* str)
{
    sigset_t sigset;
    int errno_save;

    /* we can be called by signal handlers */
    errno_save=errno;
    if(sigprocmask(0,NULL,&sigset)<0){
        fprintf(stderr,"sigprocmask error.\n");
    }
    else{
        printf("%s",str);
        if(sigismember(&sigset,SIGINT))
            printf(" SIGINT");
        if(sigismember(&sigset,SIGQUIT))
            printf("SIGQUIT");
        if(sigismember(&sigset,SIGUSR1))
            printf("SIGUSR1");
        if(sigismember(&sigset,SIGUSR2))
            printf("SIGUSR2");

        printf("\n");
    }

    errno=errno_save;   /* restore errno */
}
```

函数`sigpending`可以获取对当前进程未决的信号集

```cpp
#include<signal.h>
int sigpending(sigset_t *set);
```

##### 实例：信号设置和sigprocmask实例

```cpp
#include<stdio.h>
#include<unistd.h>
#include<signal.h>

static void sig_quit(int);

int main(void)
{
    sigset_t newmask,oldmask,pendmask;

    if(signal(SIGQUIT,sig_quit)==SIG_ERR)
        fprintf(stderr,"can't catch SIGQUIT.\n");

    sigemptyset(&newmask);
    sigaddset(&newmask,SIGINT);

    if(sigprocmask(SIG_BLOCK,&newmask,&oldmask)<0)
        fprintf(stderr,"SIG_BLOCK error.\n");

    sleep(5);

    if(sigpending(&pendmask)<0)
        fprintf(stderr,"sigpending error.\n");
    if(sigismember(&pendmask,SIGINT))
        printf("SIGQUTI pending.\n");

    //sigprocmask只是暂时将信号置于未决状态
    //当将信号从信号屏蔽字移除后，会传递到进程
    if(sigprocmask(SIG_SETMASK,&oldmask,NULL)<0)
        fprintf(stderr,"SIG_SETMASK error.\n");

    printf("SIGQUIT unblocked.\n");

    sleep(5);
    exit(0);
}

static void
sig_quit(int signo)
{
    printf("caught SIGQUIT\n");
    if(signal(SIGQUIT,SIG_DFL)==SIG_ERR)
        fprintf(stderr,"can't reset SIGQUIT.\n");
}
```

`sigaction`函数的功能是检查或修改与指定信号向关联的处理动作。此函数取代了UNIX早期版本使用的`signal`函数

```cpp
#include<signal.h>

//act非空则修改信号，否则查看该信号的上一个动作
int sigaction(int signo,const struct sigaction* restrict act,struct sigaction* restrict oact);
```

关于`sigaction`有以下几点需要注意:

1. 可以将触发事件的信号加入到信号屏蔽字(`signal`是默认)
2. 阻塞了发生多次的信号，当该信号解除阻塞时，只被传递一次（除非对该信号进行了排队处理）
3. 触发信号处理函数后，信号处理方式不会恢复为默认

#### 函数sigsetjmp和siglongjmp

在信号处理程序中经常调用`longjmp`函数以返回到程序的主循环中，而不是从该处理程序返回。但是由于进入信号处理程序时，当前信号是被屏蔽的，从信号处理程序返回时该信号是否还被屏蔽是不确定的,为了避免这种不确定性，我们使用`sigsetjmp/siglongjmp`来替代`setjmp/longjmp`

```cpp
#include<setjmp.h>

int sigsetjmp(sigjmp_buf env,int savemask);     //savemask非0时恢复保存的信号屏蔽字
void siglongjmp(sigjmp_buf env,int val);        //val是jump之后的返回值

```

##### 实例：使用siglongjmp恢复信号屏蔽字

```cpp
#include<stdio.h>
#include<unistd.h>
#include<setjmp.h>
#include<time.h>
#include<signal.h>
#include<errno.h>

#define oops(m,x) { perror(m); exit(x); }

static void sig_usr1(int);
static void sig_alrm(int);
static sigjmp_buf jmpbuf;
static volatile sig_atomic_t canjump;

void pr_mask(const char* str)
{
    sigset_t sigset;
    int errno_save;

    /* we can be called by signal handlers */
    errno_save=errno;
    if(sigprocmask(0,NULL,&sigset)<0){
        fprintf(stderr,"sigprocmask error.\n");
    }
    else{
        printf("%s",str);
        if(sigismember(&sigset,SIGINT))
            printf(" SIGINT");
        if(sigismember(&sigset,SIGQUIT))
            printf(" SIGQUIT ");
        if(sigismember(&sigset,SIGUSR1))
            printf(" SIGUSR1 ");
        if(sigismember(&sigset,SIGUSR2))
            printf(" SIGUSR2 ");
        if(sigismember(&sigset,SIGALRM))
            printf(" SIGALRM ");

        printf("\n");
    }

    errno=errno_save;   /* restore errno */
}


int main(void)
{
    if(signal(SIGUSR1,sig_usr1)==SIG_ERR)
        oops("signal(SIGUSR1) error.\n",1);
    if(signal(SIGALRM,sig_alrm)==SIG_ERR)
        oops("signal(SIGALRM) error.\n",2);

    pr_mask("starting main: ");

    if(sigsetjmp(jmpbuf,1)){
        pr_mask("ending main: ");
        exit(0);
    }

    canjump=1;

    for(;;)
        pause();
}

static void
sig_usr1(int signo)
{
    time_t starttime;

    if(canjump==0)
        return;

    pr_mask("starting sig_usr1: ");

    alarm(3);
    starttime=time(NULL);
    for(;;)
        if(time(NULL)>starttime+5)
            break;

    pr_mask("finishing sig_usr1: ");

    canjump=0;
    siglongjmp(jmpbuf,1);
}

static void
sig_alrm(int signo)
{
    pr_mask("in sig_alrm: ");
}
```

上述程序输出:

![avatar](../image/../../image/unix_10_10_20.jpg)


#### 函数abort

`abort`函数的功能是使程序异常终止，此函数将`SIGABRT`信号发送给调用进程（进程不应忽略此信号）

```cpp
#include<stdlib.h>

//发送SIGABRT给调用进程，并要求该进程执行相应的信号处理函数，且进程应在该信号处理函数中结束自己
void abort(void);
```

#### 函数sleep

`sleep`函数使得程序挂起

```cpp
#include<unistd.h>

//返回值：0或未休眠完的秒数
unsigned int sleep(unsigned int seconds);

```

`sleep`函数并不是可靠，当以下两个条件发生时该函数会释放挂起的进程:

1. 已经过了seconds所指定的墙上时钟时间
2. 调用进程捕捉到一个信号并从信号处理程序返回

#### 作业控制信号

POSIX.1认为有以下6个与作业控制有关的信号:

* `SIGCHLD`: 子进程已停止或终止
* `SIGCONT`: 如果进程已停止，则使其继续运行
* `SIGSTOP`: 停止信号（不能被捕捉或忽略）
* `SIGTSTP`: 交互式停止信号
* `SIGTTIN`: 后台进程组成员读控制终端
* `SIGTTOU`: 后台进程组成员写控制终端

在作业控制信号间有某些交互。当对一个进程产生4种停止信号(`SIGTSTP`,`SIGSTOP`,`SIGTTIN`或`SIGTTOU`)中的任意一种时，对该进程的任一未决`SIGCONT`信号就被丢弃。与此类似，当对一个进程产生`SIGCONT`信号时，对同一进程的任一未决停止信号被丢弃

#### 常见信号总结

| 信号 | 说明 |
| :---: | :---: |
| SIGABRT | 调用abort函数产生此信号，使得进程异常终止 |
| SIGALRM | 当用alarm函数设置的定时器超时时产生此信号 |
| SIGCHLD | 在一个进程终止或停止时，发送此信号给给其父进程 |
| SIGCONT | 此作业控制信号发送给处于停止状态需要继续运行的进程 |
| SIGINT | 当用户按中断键(`Ctrl+C`)时，终端驱动程序产生此信号并发送给前台进程组中的每个进程 |
| SIGPIPE | 如果在管道的读进程已终止时写管道，则产生此信号 |
| SIGQUIT | 当用户在终端上按退出键(`ctr\`)时，中断驱动程序产生此信号，并发送给前台进程组中的所有进程 |
| SIGSTOP | 这是一个作业控制信号，它停止一个进程 |
| SIGTERM | 这是由kill命令发送的系统默认终止信号 |
| SIGTSTP | 交互停止信号 |
| SIGTTIN | 当一个后台进程组进程试图读其控制终端时，终端驱动程序产生此信号 |
| SIGTTOU | 当一个后台进程组进程试图写其控制终端时，终端驱动程序产生此信号 |
| SIGUSR1 |  这是一个用户定义的信号，可用于应用程序 |
| SIGUSR2 |  这是一个用户定义的信号，可用于应用程序 |