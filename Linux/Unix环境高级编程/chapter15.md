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

