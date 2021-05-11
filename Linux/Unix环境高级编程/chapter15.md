[toc]

### chapter15 进程间通信

#### 引言

进程间通信(`InterProcess Communication ,IPC`),包括`管道`、`命名管道(FIFO)`和XSI IPC的三种形式IPC(`消息队列`、`信号量`和`共享存储`),以及POSIX提供的替代信号量机制。

#### 管道

```cpp
//创建管道
int pipe(int fd[2]);    //fd[0]为读端，fd[1]为写端
```

所有UNIX系统都提供了管道通信，管道有以下两点限制:一是它们是半双工的，现在某些系统提供全双工的管道；二是管道只能在具有公共祖先的两个进程之间使用。

当管道的一端被关闭后，下列两条规则其作用:

1. 当读(read)一个写端已被关闭的通道时，在所有数据都被读取后，read返回0，表示文件结束。
2. 如果写(write)一个读端已被关闭的管道，则产生信号SIGPIPE。如果忽略该信号或者捕捉该信号并从其处理程序返回，则write返回-1,errno设置为EPIPE。

常见的操作是创建一个连接到另一个进程的管道，然后读其输出或向其输入端发送数据，为此，标准I/O库提供了两个函数`popen`和`pclose`.这两个函数实现的操作是：创建一个管道，fork一个子进程，关闭未使用管道端，执行一个shell运行命令，然后等待命令终止。

```cpp
//若type是“r”，则文件指针连接到cmdstring的标准输出
//若type是"w"，则文件指针连接到cmdstring的标准输入
FILE* popen(const char* cmdstring,const char* type);
int pclose(FILE* fp);
```

#### FIFO

```cpp
//创建FIFO
int mkfifo(const char* path,mode_t mode);
int mkfifoat(int fd,const char* path,mode_t mode);
```

FIFO有时被称为命名管道。未命名的管道只能在两个相关的进程之间使用，而且这两个相关的进程还要有一个共同的创建了它们的祖先进程。但是，通过FIFO,不相关的进程也能交换数据。

类似于管道，若write一个尚无进程为读而打开的FIFO，则产生信号SIGPIPE。若某个FIFO的最后一个写进程关闭了该FIFO,则将为该FIFO的读进程产生一个文件结束标志。

当open一个FIFO时，非阻塞标志(O_NONBLOCK)会产生下列影响:

1. 没有指定O_NONBLOCK:只读open要阻塞到某个其他进程为写而打开这个FIFO为止。类似地，只写open要阻塞到某个其他进程为读而打开它为止。
2. 如果指定O_NONBLOCK:此时只读open离开返回。但是，如果没有进程为读而打开一个FIFO,那么只写open将返回-1,并将errno设置成ENXIO。

#### XSI IPC

有3种称为XSI IPC的IPC:消息队列、信号量以及共享存储。

**每个内核中的IPC结构都用一个非负整数的标识符加以引用**。与文件描述符不同，IPC标识符不是小的整数，当一个IPC结构被创建，然后又被删除时，与这种结构相关的标识符连续加1，直至到达一个整型数的最大正值，然后回转到0.

可以通过`ftok`函数由一个路径名和项目ID产生一个键:

```cpp
//由路径名和项目ID产生一个标识符键
key_t ftok(const char* path,int id);
```

XSI IPC还为每个IPC结构关联了一个ipc_perm结构，该结构规定了权限和所有者，它至少包括下列成员:

```cpp
struct ipc_perm{
    uid_t uid;
    gid_t gid;
    uid_t cuid;
    gid_t cgid;
    mode_t mode;
    //...
};
```

#### 消息队列

消息队列是消息的链接表，存储在内核中，由消息队列标识符标识，这里我们将队列简称为队列，其标识符简称为`队列ID`。

消息队列相关的函数如下:

```cpp
int msgget(key_t key,int flag);                                     //打开或创建队列,若成功，返回消息队列ID
int msgctl(key_t key,int cmd,struct msqid_ds* buf);                 //控制队列
int msgsnd(int msqid,const void* ptr,size_t nbytes,int flag);       //放数据到消息队列
int msgrcv(int msqid,void* ptr,size_t nbytes,long type,int flag);   //从队列中取消息
```

消息队列除了按序读取消息，还可以读取指定的消息。

#### 信号量

信号量是一个计数器，用于为多个进程提供对共享数据对象的访问。

为了获得共享资源，进行需要执行下列操作:

1. 测试控制该资源的信号量
2. 若此信号量的值为正，则进程可以使用该资源。在这种情况下，进程会将信号量减1，表示它使用了一个资源单位。
3. 否则，若此信号量的值为0，则进程进入休眠状态，直至信号量值大于0。进程被唤醒后，它返回至步骤(1)。

当进程不再使用由一个信号量控制的共享资源时，该信号量增1。如果有进程正在休眠等待此信号量，则唤醒它们。

XSI信号量相关的函数如下:

```cpp
int semget(key_t key,int nsems,int flag);                           //引用或创建一个信号量集
int semctl(int semid,int semnum,int cmd,.../* union semun arg */)   //控制信号量
int semop(int semid,struct sembuf semoparray[],size_t nops);        //操作信号量
```

无论何时只要为信号量操作指定了`SEM_UNDO`标志，然后分配资源(sem_op值小于0)，那么内核就会记住对于该特定信号量，分配给调用进程多少资源(sem_op的绝对值)。当该进程终止时，不论自愿或者不自愿，内核都将检验该进程是否还有尚未处理的信号量调整值，如果有，则按调整值对相应信号量进行处理。(相比于互斥量，如果一个进程没有释放互斥量而终止，恢复将是非常困难的)

#### 共享存储

共享存储允许两个或多个进程共享一个给定的存储区。因为数据不需要在客户进程和服务器进程之间复制，所以这是最快的一种IPC。

与共享存储相关的函数如下:

```cpp
int shmget(key_t key,size_t size,int flag);                         //获得一个共享存储,若成功，返回共享存储ID
int shmctl(int shmid,int cmd,struct shmid_ds* buf);                 //控制共享存储
void* shmat(int shmid,const void* addr,int flag);                   //将共享存储连接到进程的地址空间
int shmdt(const void* addr);                                        //断开与共享存储的连接
```

当对共享存储段的操作已经结束时，则调用shmdt与该段分离，此时将连接到该共享存储段的进程数减1。直至某个进程带IPC_RMID命令的调用shmctl特地删除该共享存储为止。

#### POSIX信号量

POSIX信号量接口意在解决XSI信号量接口的几个缺陷：

1. 相比于XSI接口，POSIX信号量接口考虑到了更高性能的实现。
2. POSIX信号量接口使用更简单：没有信号量集。
3. POSIX信号量在删除时表现更完美。当一个XSI信号量被删除时，使用这个信号量标识符的操作会失败，并将errno设置EIDRM。使用POSIX信号量时，操作能继续正常工作直到该信号量的最后一次引用被释放。

POSIX信号量相关的函数如下:

```cpp
sem_t* sem_open(const char* name,int oflag,.../*mode_t mode,unsigned int value */);         //创建或使用一个命令信号量，成功时返回指向信号量的指针
int sem_unlink(conat char* name);       //销毁一个命名信号量
int sem_close(sem_t* sem);              //释放信号量
int sem_trywait(sem_t *sem);            //信号量减1操作
int sem_wait(sem_t* sem);               //信号量减1操作
int sem_post(sem_t* sem);               //信号量增1操作
int sem_init(sem_t* sem,int pshared,unsigned int value);            //创建一个未命名的信号量
int sem_destroy(sem_t* sem);                                        //销毁一个未命名信号量
int sem_getvalue(sem_t* restrict sem,int *restrict valp);           //获取信号量值
```


