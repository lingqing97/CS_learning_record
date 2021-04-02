[toc]

### chapter11 线程

#### 线程概念

每个线程都包含表示执行环境所必需的信息，其中包括进程中标识线程的线程ID、一组寄存器值、栈、调度优先级和策略、信号屏蔽字、errno变量以及线程私有数据。

一个进程的所有信息对该进程的所有线程都是共享的，包括可执行程序的代码、程序的全局内存和堆内存、栈以及文件描述符

#### 线程标识


进程ID在整个系统中是唯一的，但线程ID不同，线程ID只有在它所属的进程上下文中才有意义。

```cpp
#include<pthread.h>

int pthread_equal(pthread_t tid1,pthread_t tid2);   //比较两个线程ID是否相等

pthread_t pthread_self(void);   //获取线程ID
```

#### 线程创建

新增的线程可以通过调用`pthread_create`函数创建

```cpp
#include<pthread.h>

/*
tidp: 指向创建的线程ID
attr: 设置线程属性
start_rtn:与线程绑定的函数
arg:传入函数的参数
*/
int pthread_create(pthread_t* restrict tidp,
                    const pthread_att_t* restrict attr,
                    void *(*start_rtn)(void*),void* restrict arg);
```

##### 实例：打印线程ID

```cpp
#include<stdio.h>
#include<unistd.h>
#include<pthread.h>


pthread_t ntid;


void printids(const char* s)
{
    pid_t pid;
    pthread_t tid;

    pid=getpid();
    //这里注意，不能直接使用ntid获取线程ID
    //如果新线程在主线程调用pthread_create返回之前就运行了，那么新线程看到的是未经初始化的ntid的内容，这个内容并不是正确的线程ID
    tid=pthread_self();
    printf("%s pid %lu tid %lu (0x%1x)\n",s,(unsigned long)pid,(unsigned long)tid,(unsigned long)tid);
}

void* thr_fn(void* arg)
{
    printids("new thread: ");
    return ((void*)0);
}

/*
输出:
main thread:  pid 6068 tid 140266621622080 (0x5e27d740)
new thread:  pid 6068 tid 140266613135104 (0x5da65700)
*/

int main(void)
{
    int err;

    err=pthread_create(&ntid,NULL,thr_fn,NULL);
    if(err!=0)
    {
        fprintf(stderr,"cant't create thread\n");
        exit(1);
    }
    printids("main thread: ");
    sleep(1);
    exit(0);
}
```

#### 线程终止

**如果进程中的任意线程调用了`exit`、`_Exit`或者`_exit`,那么整个进程就会终止**

单个线程可以通过以下3种方式退出，因此可以在不终止整个进程的情况下，停止它的控制流：

1. 线程可以简单地从启动例程中返回，返回值是线程的退出码
2. 线程可以被同一进程中的其他线程取消
3. 线程调用`pthread_exit`

```cpp
#include<pthread.h>

void pthread_exit(void* rval_ptr);

//调用线程将一直阻塞，直到指定的线程调用pthread_exit、从启动例程中返回或者被取消
int pthread_join(pthread_t thread,void **rval_ptr);

//注意pthread_cancel并不等待线程终止，它仅仅提出请求
int pthread_cancel(pthread_t tid);
```

##### 实例：获取线程退出状态

```cpp
#include<stdio.h>
#include<stdlib.h>
#include<pthread.h>

void* thr_fn1(void* arg)
{
    printf("thread 1 returning\n");
    return ((void*)1);
}

void* thr_fn2(void* arg)
{
    printf("thread 2 exiting\n");
    pthread_exit((void*)2);
}

/*
输出:
thread 1 returning
thread 2 exiting
thread 1 exit code 1
thread 1 exit code 2
*/

int main(void)
{
    int err;
    pthread_t tid1,tid2;
    void *tret;

    err=pthread_create(&tid1,NULL,thr_fn1,NULL);
    if(err!=0){
        fprintf(stderr,"can't create pthread 1\n");
        exit(1);
    }
    err=pthread_create(&tid2,NULL,thr_fn2,NULL);
    if(err!=0){
        fprintf(stderr,"can't create pthread 1\n");
        exit(2);
    }
    err=pthread_join(tid1,&tret);
    if(err!=0){
        fprintf(stderr,"can't join with pthread 1\n");
        exit(3);
    }
    printf("thread 1 exit code %ld\n",(long)tret);
    err=pthread_join(tid2,&tret);
    if(err!=0){
        fprintf(stderr,"can't join with pthread 2\n");
        exit(4);
    }
    printf("thread 1 exit code %ld\n",(long)tret);
    exit(0);
}
```

`pthread_create`和`pthread_exit`函数的无类型指针参数可以传递的值不止一个，这个指针可以传递包含复杂信息的结构的地址，但是注意，这个结构所使用的内存在调用者完成调用以后必须仍然是有效的。

#### 线程同步

##### 互斥量

`互斥量(mutex)`从本质上说是一把锁，在访问共享资源前对互斥量进行设置(加锁)，在访问完成后释放(解锁)互斥量。对互斥量进行加锁以后，任何其他试图再次对互斥量加锁的线程都会被阻塞直到当前线程释放该互斥量。

如果释放互斥量时有一个以上的线程阻塞，那么所有该锁上的阻塞线程都会变成可运行状态，第一个变为运行的线程就可以对互斥量加锁，其他线程就会看到互斥量依然是锁着的，只能回去再次等待它重新变为可用。

互斥量可以通过`pthread_mutex_init`进行初始化，静态分配的互斥量还可以将其设置为常量`PTHREAD_MUTEX_INITIALIZER`,对于动态分配的互斥量，在释放内存前需要调用`pthread_mutex_destory`。

```cpp
#include<pthread.h>

int pthread_mutex_init(pthread_mutex_t* restrict mutex,const pthread_mutexattr_t* restrict attr);

int pthread_mutex_destory(pthread_mutex_t* mutex);

//加锁
int pthread_mutex_lock(pthread_mutex_t* mutex);
//尝试对互斥量进行加锁，如果互斥量处于未锁状态则锁住互斥量；否则加锁失败，返回EBUSY
int pthread_mutex_trylock(pthread_mutex_t* mutex);
//解锁
int pthread_mutex_unlock(pthread_mutex_t* mutex);

//可以设置阻塞时间段的加锁,这里的时间是绝对时间，而不是相对时间
int pthread_mutex_timedlock(pthread_mutex_t *restrict mutex,
                            const struct timespec* restrict tsptr);
```

当有多个互斥量时，非常容易发生死锁，可以通过仔细控制互斥量加锁的顺序来避免死锁的发生。

##### 实例: 使用互斥量保护数据结构

```cpp
#include<stdlib.h>
#include<pthread.h>

/*
    使用互斥量保护数据结构
*/

struct foo{
    int     f_count;
    pthread_mutex_t f_lock;
    int     f_id;
};

struct foo*
foo_alloc(int id) /* allocate the object */
{
    struct foo* fp;
    if((fp=malloc(sizeof(struct foo)))!=NULL){
        fp->f_count=1;
        fp->f_id=id;
        if(pthread_mutex_init(&fp->f_lock,NULL)!=0){
            free(fp);
            return NULL;
        }
    }
    return fp;
}

void foo_hold(struct foo *fp) /* add a reference to the object */
{
    pthread_mutex_lock(&fp->f_lock);
    fp->f_count++;
    pthread_mutex_unlock(&fp->f_lock);
}

void
foo_rele(struct foo* fp) /* release a reference to the object */
{
    pthread_mutex_lock(&fp->f_lock);
    if(--fp->f_count==0){
        pthread_mutex_unlock(&fp->f_lock);
        pthread_mutex_destory(&fp->f_lock);
        free(fp);
    }
    else{
        pthread_mutex_unlock(&fp->f_lock);
    }
}
```

##### 读写锁(也叫做共享互斥锁)

`读写锁`与互斥量类似，不过读写锁允许更高的并行性。

互斥量要么是锁住状态，要么就是不加锁状态，而且一次只有一个线程可以对其加锁。读写锁可以有3种状态：**读模式下加锁状态，写模式下加锁状态，不加锁状态**。一次只有一个线程可以占有写模式的读写锁，但是多个线程可以同时占有读模式的读写锁。

当读写锁是**写加锁**状态时，在这个锁被解锁之前，所有试图对这个锁加锁的线程都会被阻塞。当读写锁在读加锁状态时，所有试图以读模式对它进行加锁的线程都可以得到访问权，但是任何希望以写模式对此锁进行加锁的线程都会阻塞，直到所有线程释放它们的读锁为止。

读写锁非常适合对数据结构读的次数远大于写的情况。

```cpp
#include<pthread.h>

int pthread_rwlock_init(pthread_rwlock_t* restrict rwlock,
                        const pthread_rwlockattr_t* restrict attr);

int pthread_rwlock_destory(pthread_rwlock_t* rwlock);   //释放动态分配的读写锁

//使用下列函数记得要对返回值进行错误检查
int pthread_rwlock_rdlock(pthread_rwlock_t* rwlock);    //读加锁

int pthread_rwlock_wrlock(pthread_rwlock_t* rwlock);    //写加锁

int pthread_rwlock_unlock(pthread_rwlock_t* rwlock);    //解锁
```

与互斥量一样, Single UNIX Specification提供了带有超时的读写锁加锁函数:

```cpp
#include<pthread.H>
#include<time.h>


//和互斥量一样，这里使用的也是绝对时间，而不是相对时间
int pthread_rwlock_timedrdlock(pthread_rwlock_t* restrict rwlock,
                                const struct timespec* restrict tsptr);

int pthread_rwlock_timedwrlock(pthread_rwlock_t* restrict rwlock,
                                const struct timespec* restrict tsptr);
```

#### 条件变量

与互斥量的应用场景不同，条件变量是用来等待而不是用来上锁的，条件变量用来自动阻塞一个线程，直到某些特殊情况发生为止.同时，条件变量总是和一个互斥量绑定，从而保证条件发生时信号不会被丢失。

```cpp
#include<pthread.h>

//初始化
int pthread_cond_init(pthread_cont_t* restrict cond,
                        const pthread_condattr_t* restrict attr);
//释放内存
int pthread_cond_destory(pthread_cond_t* cond);

//调用者需要将加锁的互斥量传给wait函数，pthread_cond_wait内部会对互斥量解锁，返回时会再次锁住互斥量
//阻塞等待
int pthread_cond_wait(pthread_cond_t* restrict cond,
                        pthred_mutex_t* restrict mutex);

//超时等待
int pthread_cond_timedwait(pthread_cond_t* restrict cond,
                            pthread_mutex_t* restrict mutex,
                            const struct timespec* restrict tsptr);

//唤醒阻塞的一个线程
int pthread_cond_signal(pthread_cond_t* cond);
//唤醒所有线程
int pthread_cond_broadcast(pthread_cond_t* cond);
```

##### 实例：使用条件变量

```cpp
#include<pthread.h>

struct msg{
    struct msg* mnext;
    /* ...more stuff here... */
};

struct msg* workq;

pthread_cond_t qready=PTHREAD_COND_INITIALIZER;
pthread_mutex_t qlock=PTHREAD_MUTEX_INITIALIZER;

//从队列中取一个元素
void process_msg(void)
{
    struct msg* mp;
    for(;;){
        pthread_mutex_lock(&qlock);
        while(workq==NULL)      //队列为空，等待条件发生
            pthread_cond_wait(&qready,&qlock);
        mp=workq;
        workq=mp->m_next;
        pthread_mutex_unlock(&qlock);
    }
}

//入队列一个元素
void enqueue_msg(struct msg* mp)
{
    pthread_mutex_lock(&qlock);
    mp->next=workq->next;
    workq->next=mp;
    pthread_mutex_unlock(&qlock);
    pthread_cond_signal(&qready);
}
```

#### 自旋锁


自旋锁与互斥量类似，但它不是通过休眠使进程阻塞，而是在获取锁之前一直处于忙等待(自旋)阻塞状态（`忙等待`可以理解为while(true),线程并不放弃CPU,受CPU的时间调度）.自旋锁可用于以下情况：锁被持有的时间短，而且线程并不希望在重新调度上花费太多的成本。

自旋锁与互斥量的区别在于:

1. 互斥量加锁失败后，线程会释放CPU给其他线程，从而导致线程恢复时需要切换线程上下文，成本较大。
2. 自旋锁加锁失败后，线程会忙等待，直到它拿到锁，所以它不需要切换线程上下文，成本相对较小。(在单CPU无调度的情况下，自旋锁会长期占用CPU，不适用)

```cpp
#include<pthread.h>

//初始化
int pthread_spin_init(pthread_splinlock_t* lock,int pshard);
//释放内存
int pthread_spin_destory(pthread_splinlock_t* lock);

//加锁
int pthread_spin_lock(pthread_spinlock_t* lock);
int pthread_spin_trylock(pthread_spinlock_t* lock);
//解锁
int pthread_spin_unlock(pthread_spinlock_t* lock);
```

#### 屏障

`屏障(barrier)`是用户协调多个线程并行工作的同步机制。之前，我们已经看到一种屏障，`pthread_join`函数就是一种屏障，运行一个线程等待，直到另一个线程退出。但是屏障对象的概念更广，它们允许任意数量的线程等待，直到所有的线程完成处理工作，而线程不需要退出。所有线达到屏障后可以接着工作。

```cpp
#include<pthread.h>

//初始化
int pthread_barrier_init(pthread_barrier_t* restirct barrier,
                        const pthread_barrierattr_t* restrict attr,
                        unsigned int count);    //count指定需要等待的线程数
//这里的destory释放init的屏障,而不只是动态分配的
int pthread_barrier_destroy(pthread_barrier_t* barrier);

//等待,每调用该函数一次，屏障计数加一
int pthread_barrier_wait(pthread_barrier_t* barrier);
```

调用`pthread_barrier_wait`的线程在屏障计数未满足条件时，会进入休眠状态。如果该线程是最后一个调用`pthread_barrier_wait`的线程，就满足了屏障计数，所有的线程都被唤醒。

#### 乐观锁与悲观锁

悲观锁做事比较悲观，它认为多线程同时修改共享资源的概率较高，于是容易出现冲突，所以访问共享资源前先要上锁。之前提到的互斥量、自旋锁、读写锁都是悲观锁。

乐观锁做事比较乐观，它假设冲突的概率很低，它的工作方式是：先修改完共享资源，再验证这段时间内有无冲突，如果没有其他线程在修改资源，那么操作完成，如果发现有其他线程已经修改过这个资源，就放弃本次操作。
