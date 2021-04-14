[toc]

### chapter12 线程控制

#### 线程属性

每个线程对象可以关联一个属性对象，该属性对象通过初始化函数初始化，通过销毁函数销毁，可以通过相关取值/设值函数读取/修改属性值。

```cpp
#include<pthread.h>

//两个函数的返回值：若成功，返回0；否则，返回错误编号
int pthread_attr_init(pthread_attr_t* attr)         //初始化线程属性
int pthread_attr_destroy(pthread_attr_t* attr)      //销毁线程属性
```

`POSIX.1`中线程有以下属性:

1. 线程的分离状态属性(`detachstate`)：分离线程是指，如果对现有的某个线程的终止状态不感兴趣的话，可以使用`pthread_detach`函数让操作系统在线程退出时收回它所占用的资源，而不需要进程来管理
2. 线程栈末尾的警戒缓冲区大小(`guardsize`)：该属性控制着线程栈末尾之后用以避免栈溢出的扩展内存的大小，如果线程的栈指针溢出到警戒区域，应用程序就可能通过信号接收到出错信息
3. 线程栈的最低地址(`stackaddr`)：该属性描述线程的最低内存地址，但这并不一定是栈的开始位置。对于有一些处理器，栈是从高地址向低地址方向增长的，那么此时该属性将是栈的结尾位置，而不是开始位置
4. 线程栈的最小长度(`stacksize`)：有时线程栈的虚地址空间不够用，这时可以设置线程栈的最小长度
5. 可取消状态：通过该属性控制线程是否可以通过`pthread_cancel`取消
6. 可取消类型: 取消类型分为`推迟取消`和`异步取消`,我们所描述的默认取消类型是`推迟取消`,此时调用`pthread_cancel`以后，在线程到达取消点之前，并不会出现真正的取消。而使用`异步取消`时，线程可以在任意时间撤销，不是非得遇到取消点才能被取消

#### 线程特定数据

`线程特定数据`，也被称为线程私有数据，是存储和查询某个特定线程相关数据的一种机制。我们把这种数据称为线程特定数据或线程私有数据的原因是，我们希望每个线程可以访问它自己单独的数据副本，而不需要担心与其他线程的同步访问问题。

比如,`errno`就被定义为线程私有数据，这样，一个线程做了重置`errno`的操作也不会影响进程中其他线程的`errno`值。

#### 同步属性

就像线程具有属性一样，线程的同步对象也有属性。

互斥量有三个属性：`进程共享属性`、`健壮属性`以及`类型属性`.

1. 进程共享属性：在多进程中存在这样的机制，允许相互独立的多个进程把同一个内存数据块映射到它们各自独立的地址空间中，就像多个线程访问共享数据一样，多个进程访问共享数据通常也需要同步。如果互斥量的进程共享属性设置为`PTHREAD_PROCESS_SHARD`,从多个进程彼此之间共享的内存数据块中分配的互斥量就可以用于这些进程的同步
2. 健壮属性：该属性与多个进程共享的互斥量有关。当持有互斥量的某个进程终止时，需要解决互斥量状态恢复的问题。而健壮属性就是用于处理这类问题的
3. 类型属性：类型属性控制着互斥量的锁定特性,常用的属性是`PTHREAD_MUTEX_RECURSIVE`将互斥量设置为递归互斥量（`递归互斥量`维护锁的计数，在解锁次数和加锁次数不相同的情况下，不会释放锁）

```cpp
#include<pthread.h>

//两个函数的返回值：若成功，返回0；否则，返回错误编号
int pthread_mutexattr_init(pthread_mutexattr_t* attr)       //初始化互斥量属性
int pthread_mutexattr_destroy(pthread_mutexattr_t* attr)    //销毁互斥量属性
```

对于其他同步对象，自旋锁只有一个进程共享属性，条件变量有进程共享属性和时钟属性(`时钟属性`控制计算`pthread_cond_timedwait`函数的超时参数时采用的是哪个时钟)，读写锁只有一个进程共享属性。


#### 重入

如果一个函数在相同的时间点可以被多个线程安全地调用，就称该函数是`线程安全`的。要使函数是线程安全的，就需要将存放在静态存储区域的数据转移到线程自己提供的缓冲区中。

##### 例子:getenv的线程安全版本

`getenv`函数获取环境变量表中的值。

```cpp
#include<string.h>
#include<errno.h>
#include<pthread.h>
#include<stdlib.h>

extern char **environ;

pthread_mutex_t env_mutex;

static pthread_once_t init_done=PTHREAD_ONCE_INIT;

static void
thread_init(void)
{
    pthread_mutexattr_t attr;

    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr,PTHREAD_MUTEX_RECURSIVE);
    pthread_mutexattr_init(&env_mutex,&attr);
    pthread_mutexattr_destroy(&attr);
}

int getenv_r(const char* name,char* buf,int buflen)
{
    int i,len,olen;
    //pthread_once保证系统只调用thread_init一次，具体是哪个线程有系统调度决定
    pthread_once(&init_done,thread_init);
    len=strlen(name);
    pthread_mutex_lock(&env_mutex);
    for(i=0;environ[i]!=NULL;++i){
        if((strncmp(name,environ[i],len)==0) && (environ[i][len]=='='))
        {
            olen=strlen(&environ[i][len+1]);
            if(olen>=buflen){
                pthread_mutex_unlock(&env_mutex);
                return(ENOSPC);
            }
            strcpy(buf,&environ[i][len+1]);
            pthread_mutex_unlock(&env_mutex);
            return(0);
        }
    }
    pthread_mutex_unlock(&env_mutex);
    return(ENOENT);
}
```
