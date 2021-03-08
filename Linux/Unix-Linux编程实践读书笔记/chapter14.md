### chapter14 线程机制：并发函数的使用

#### 章节知识总结

多个线程在一个单独的进程中运行，共享全局变量，因此线程间可以通过设置和读取这些全局变量来进行通信。线程的执行顺序是无法预测的。下面是一个多线程的例子：

```cpp
#include<stdio.h>
#include<pthread.h>

#define NUM 5

void* print_msg(void*);

int main()
{
    pthread_t pid1,pid2;
    pthread_create(&pid1,NULL,print_msg,(void*)"hello ");
    pthread_create(&pid2,NULL,print_msg,(void*)"world\n");

    //等待线程pid1和pid2的结束
    pthread_join(pid1,NULL);
    pthread_join(pid2,NULL);

    return 0;
}

void* print_msg(void* msg)
{
    char* cp=(char*) msg;
    int i;
    for(i=0;i<NUM;++i){
        printf("%s",cp);
        fflush(stdout);
        sleep(1);
    }
    return;
}
```

在上面的程序中使用`pthread_join`函数来等待线程返回。每个线程都占用了系统资源。如果程序员忘记使用`pthread_join`来收回线程，这些线程所占用的资源就无法被回收。

可以创建一种不需要等待返回的线程，这种线程称为`独立线程`。当函数执行完毕之后，独立线程自动释放它所占用的所有的资源，它们自身甚至也不允许等待其他的线程返回。

创建一个独立线程的代码如下:

```cpp
/* creating a detached thread */
pthread_t t;
pthread_attr_t attr_detached;
pthread_attr_init(&attr_detached);
pthread_attr_setdetached(&attr_detached,PTHREAD_CREATE_DETACHED);
pthread_create(&t,&attr_detached,func,arg);
```

独立线程可以用于web服务器中：每当服务器接收一个请求，则生成一个独立线程取去处理该请求，而主程序不需要等待独立线程的返回。

进程和线程有根本上的不同，每个进程都有其独立的数据空间、文件描述符以及进程的ID。而线程共享一个数据空间、文件描述符以及进程ID。

   * 共享数据空间：多线程中可以出现的一个问题是，一个线程分配了一块空间存储一个字符串，当此线程做其他事情的时候，另一个线程使用free释放这块空间。那么原先的线程中本来指向此空间的指针现在只想了一块已经被释放的地方。
   * 共享的文件描述符：在多进程中，执行fork语句之后，文件描述符自动被复制，从而子进程得到了一套新的文件描述符。而在多线程中，多个线程共享一套文件描述符。
   * fork、exec、exit、signals：如果一个线程执行了exit,那么整个进程都将结束运行。

由于线程共享数据空间,为了避免数据读取错乱，线程系统包含了称为`互斥锁`的变量，它可以使线程间很好的合作，避免对于变量、函数以及资源的访问冲突。


可以通过`pthread_mutex_lock`和`pthread_mutex_unlock`分别来锁住和解除指定的互斥量，下面这个例子说明了互斥量在多线程中的使用:

```cpp
#include<stdio.h>
#include<pthread.h>
#include<ctype.h>

#define oops(m) { perror(m); exit(1); }

void count_word(void*);

int count=0;
pthread_mutex_t counter_lock=PTHREAD_MUTEX_INITIALIZER;

int main(int ac,char* av[])
{
    if(ac!=3){
        fprintf(stderr,"usage: undefined parameters");
        exit(1);
    }
    pthread_t pid1,pid2;
    pthread_create(&pid1,NULL,count_word,(void*)av[1]);
    pthread_create(&pid2,NULL,count_word,(void*)av[2]);
    pthread_join(pid1,NULL);
    pthread_join(pid2,NULL);

    printf("Total:%d\n",count);

    return 0;
}

void count_word(void* f)
{
    char* filename=(char*) f;
    FILE* file;
    if((file=fopen(filename,"r"))!=NULL){
        int ch='\0',pre='\0';
        while((ch=getc(file))!=EOF)
        {
            //这个判断有问题!!!
            if(!isalnum(ch)&&isalnum(pre))
                pthread_mutex_lock(&counter_lock);
                ++count;
                pthread_mutex_unlock(&counter_lock);
            pre=ch;
        }
        fclose(file);
    }
    else{
        oops(filename);
    }
}
```

如果共享数据的访问次数频繁，使用互斥量会使得程序运行速度变慢。

线程之间通过`pthread_cond_wait`和`pthread_cond_signal`来进行通信。`pthread_cond_wait`函数总是和互斥锁在一起使用。此函数先自动释放所指定的锁，然后等待条件变量的变化。如果在调用此函数之前，互斥量`mutex`并灭有被锁住，函数执行的结果是不确定的。

#### 系统调用

| | pthread_create |
| :----: | :----: |
| 用途 | 创建一个新的线程 |
| 头文件 | #include<pthread.h> |
| 函数原型 | int pthread_create(pthread_t* thread,pthread_attr_t* attr,void* (*func)(void*),void* arg); |
| 参数 | thread: 指向pthread_t类型变量的指针；attr:指向pthread_attr_t类型变量的指针，或者为NULL; func:指向新线程所运行函数的指针；arg:传递给func的参数 |
| 返回值 | 0: 成功返回 ； errcode:错误 |


| | pthread_join |
| :----: | :----: |
| 用途 | 等待某线程终止 |
| 头文件 | #include<pthread.h> |
| 函数原型 | int pthread_join(pthread_t thread,void* *retval) |
| 参数 | thread: 所等待的线程； retval:指向某存储线程返回值的变量 |
| 返回值 | 0:成功返回；errcode:错误 |

* pthread_mutex_lock():用来锁住指定的互斥量。
* pthread_mutex_unlock():用来给指定的互斥量解锁。
* pthread_cond_wait(pthread_cond_t* cond,pthread_mutex_t* mutex):使线程挂起直到另一个线程通过条件变量发出消息。
* pthread_cond_signal(pthread_cond_t* cond):通过条件变量cond发送消息