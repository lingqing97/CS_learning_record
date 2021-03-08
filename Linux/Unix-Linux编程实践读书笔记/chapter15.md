### chapter15 进程间通信(IPC)

#### 章节知识总结

`Unix`系统提供了系统调用`select`来从多个数据源读取数据，它允许程序挂起，并等待从不止一个文件描述符的输入，它的原理很简单：

1. 获得所需要的文件描述符列表
2. 将此列表传给`select`
3. `select`挂起直到任何一个文件描述符有数据到达
4. `select`设置一个变量中的若干位，用力啊通知你哪一个文件描述符已经有输入的数据

使用`select`的小demo如下:

```cpp
#include<stdio.h>
#include<sys/time.h>
#include<sys/types.h>
#include<sys/select.h>
#include<unistd.h>
#include<fcntl.h>

#define oops(m,x) { perror(m); exit(x); }

void main(int ac,char* av[])
{
    if(ac!=4)
    {
        fprintf(stderr,"usage: %s file file timeout",*av);
        exit(1);
    }

    //open files
    int fd1,fd2;
    if((fd1=open(av[1],O_RDONLY))==-1)
        oops(av[1],2);
    if((fd2=open(av[2],O_RDONLY))==-1)
        oops(av[2],3);
    //max fd plus 0
    int maxfd=1+(fd1>fd2?fd1:fd2);

    fd_set readfds;             //watch these for input
    struct timeval timeout;     //how long to wait
    while(1){
        FD_ZERO(&readfds);
        FD_SET(fd1,&readfds);
        FD_SET(fd2,&readfds);

        //set timeout value
        timeout.tv_sec=atoi(av[3]);     //set seconds
        timeout.tv_usec=0;              //no useconds

        int retval=select(maxfd,&readfds,NULL,NULL,&timeout);
        if(retval==-1)
            oops("select",4);

        if(retval>0){
            if(FD_ISSET(fd1,&readfds))
                showdata(av[1],fd1);
            if(FD_ISSET(fd2,&readfds))
                showdata(av[2],fd2);
        }
        else
            printf("no input after %d seconds\n",atoi(av[3]));
    }
}

void showdata(char* fname,int fd)
{
    char buf[BUFSIZ];
    int n;

    printf("%s:",fname);
    fflush(stdout);
    n=read(fd,buf,BUFSIZ);
    if(n==-1)
        oops(fname,5);
    write(1,buf,n);
    write(1,"\n",1);
}
```

宏`FD_ZERO`、`FD_SET`和`DF_ISSET`先将`fd_set`中所有位清除，然后为某文件描述符设置一位，再对该位进行监听。

也可以使用`poll`调用来替代`select`的功能，`select`是由Berkeley研制出来的，而`poll`则是贝尔实验室的成果。这两者完成类似的功能，而现代的大部分的Unix版本对于两者都支持。

* 通过文件通信

    服务器通过清空内容再重写的方法来更新文件。如果某客户恰好在清空和重写之间读取文件，那么它得到的将是一个空的或只有部分的内容。服务器和客户端可以使用某种类型的互斥量来避免读取数据错误，可以通过`文件锁`来解决这个问题。

* 命名管道

    通常的管道只能连接相关的进程。而使用`命名管道`可以连接不相关的进程，并且可以独立于进程存在，称这样的命名管道为`FIFO(先进先出队列)`。`命名管道`在没有人使用的时候，水管仍然是存在的。`FIFO`可以看作由文件名标志的一根水管。

    命名管道的使用:
    1. 创建FIFO:使用库函数`mkfifo(char *name,mode_t mode)`指定权限模式来创建`FIFO`.
    2. 删除FIFO:`unlink(fifoname)`函数可以用来删除FIFO.
    3. 监听FIFO的连接:`open(fifoname,O_RDONLY)`函数，`open`函数阻塞进程直到某一进程打开FIFO进行写操作.
    4. 两进程如何通过FIFO进行通信:发送进程用`write`调用,而监听进程使用`read`调用，写进程调用`close`来通知读进程通信结束.

    使用FIFO的客户/服务器程序完全**不存在竞态条件问题**：在信息的长度不超过管道的容量的情况下，`read`和`write`系统调用只是原子操作，读取操作将管道清空而写入操作又将管道塞满，因此锁机制在这里并不需要。

* 共享内存

    同一个系统里的两个进程通过使用共享的内存段来交换数据。共享的内存段是用户内存的一部分，每一个进程都有一个指向此内存段的指针。依靠访问权的设置，所有进程都可以读取这一块空间中的数据，因此进程间的资源是共享的，而不是被复制来复制去。

    共享内存段的一些基本概念如下:

    1. 共享内存段在内存中不依赖于进程的存在而存在
    2. 共享内存段有自己的名字，称为关键字(Key)
    3. 关键字是一个整型数
    4. 共享内存段有自己的拥有者以及权限位
    5. 进程可以连接到某共享内存段，并且获得指向此段的指针

    共享内存的使用:
    1. 申请共享内存段:`int seg_id=shmget(key,size-of-segmetn,flags)`,如果内存段存在，函数`shmget`找到它的位置；如果不存在，可以通过在`flags`值中指定一个创建此段和初始化权限模式的请求。
    2. 将进程连接到共享内存段:`void ptr=*shmat(seg_id,NULL,flags)`,`shmat`在进程的地址空间中创建共享内存段的部分，并返回一个指向此段的指针，`flags`参数用来指定此内存段是否为只读。
    3. 与共享内存段进行读写交互:`strcpy(ptr,"hello"); memcpy(); ptr[i]`及其他一些通用的指针操作。

    使用共享内存的时间日期服务器/客户程序如下:

```cpp
//服务器: shm_ts.c
#include<stdio.h>
#include<sys/shm.h>
#include<time.h>


#define TIME_MEM_KEY 99         //like a filename
#define SEG_SIZE ((size_t)100)  //size of segment
#define oops(m,x) { perror(m); exit(x); }

void main()
{
    int seg_id=shmget(TIME_MEM_KEY,SEG_SIZE,IPC_CREAT | 077);
    if(seg_id==-1)
        oops("shmget",1);

    char* mem_ptr=shmat(seg_id,NULL,0);

    if(mem_ptr==(void*)-1)
        oops("shmat",2);

    int n;
    long now;
    for(n=0;n<60;++n){
        time(&now);
        strcpy(mem_ptr,ctime(&now));
        sleep(1);
    }
    //now remove it
    shmctl(seg_id,IPC_RMID,NULL);
}
```

```cpp
//客户端:shm_tc.c
#include<stdio.h>
#include<sys/shm.h>
#include<time.h>


#define TIME_MEM_KEY 99
#define SEG_SIZE ((size_t)100)
#define oops(m,x) { perror(m); exit(x); }

void main()
{
    int seg_id=shmget(TIME_MEM_KEY,SEG_SIZE,0777);
    if(seg_id==-1)
        oops("shmget",1);

    char* mem_ptr=shmat(seg_id,NULL,0);
    if(mem_ptr==(void*)-1)
        oops("shmat",2);

    printf("The time, direct from memory:..%s",mem_ptr);

    shmdt(mem_ptr);
}
```

    服务器通过调用一个运行在用户空间的库函数`strcpy`来更新共享的内存段。如果客户端正好在服务器向内存段中写入新数据的时候来访问内存段，那么它可能既读到新数据也读到老数据，这里必须使用锁机制来避免这种情况的发生，内核提供了一种进程间加锁的机制，称为`信号量机制`。

Unix提供了文件锁来互斥对文件进行读写.第一种类型为写数据锁，它告诉其他进程：“**我在写文件，在完成之前任何人都必须等待**”；第二种类型的锁为读数据锁，它告诉其他进程：“**我在读文件，要写文件必须等为完成，要读文件的不受影响**”。Unix提供了3种方法锁住打开的文件:`flock`、`lockf`和`fcntl`，三者中最灵活和移植性最好的应该是`fcntl`.

下列代码为一个文件描述符设置读数据锁:

```cpp
set_read_lock(int fd)
{
    struct flock lockinfo;
    lockinfo.l_type=F_RDLCK;        //a read lock on a region
    lockinfo.l_pid=getpid();        //for ME
    lockinfo.l_start=0;             //starting 0 bytes from
    lockinfo.l_whence=SEEK_SET;     //start of file
    lockinfo.l_len=0;               //extending until EOF
    fcntl(fd,F_SETLKW,&lockinfo);
}
```

使用`fcntl(fd,F_SETLKW,&lockinfo)`,并将`lockinfo.l_type`置`F_WRLCK`

使用`fcntl(fd,F_SETLKW,&lockinfo)`,并将`lockinfo_type`置`F_UNLCK`

使用`fcntl(fd,F_SETLKW,&lockinfo)`,并将`lockinfo.l_start`置为开始位置的偏移量，同时将`lockinfo.l_len`置为区域的长度

> 注意：进程可以忽略锁机制，当别的进程设置了文件锁的时候，其他进程可以忽略它，仍旧继续原来的读取或是修改操作。(**Unix的锁机制允许进程通过这种方式合作，但并不强迫它们一定要用**)

`信号量`是一个内核变量，它可以被系统中的任何进程所访问。进程间可以使用这个变量来协调对于共享内存和其他资源的访问。

通过`semget`创建信号量集，通过`semop`对信号量进行一组操作，下面以时间/日期服务器和客户端程序进行说明:

定义信号量`number_of_writers`和`number_of_readers`，在修改共享内存之前，服务器必须先对信号量进行操作:
[0] 等候num_readers变成0
[1] 将num_writers加1
当服务器完成写操作之后，它必须对信号量再进行操作:
[0] 将num_writers减1

在客户读取共享内存之前，客户端必须先对信号量进行操作:
[0] 等待num_writers变成0
[1] 将num_readers加1
当客户完成任务之后，需要对信号量进行操作:
[0] 将num_readers减1


```cpp
//服务端: shm_ts2.c
#include<stdio.h>
#include<sys/shm.h>
#include<time.h>
#include<sys/types.h>
#include<sys/sem.h>
#include<signal.h>


#define TIME_MEM_KEY 99
#define TIME_SEM_KEY 9900
#define SEG_SIZE ((size_t)100)
#define oops(m,x) { perror(m); exit(x); }

union semun { int val; struct semid_ds* buf; ushort* array; };
int seg_id,semset_id;
void cleanup(int);

void main()
{
    int seg_id=shmget(TIME_MEM_KEY,SEG_SIZE,IPC_CREAT | 0777);
    if(seg_id==-1)
        oops("shmget",1);

    char* mem_ptr=shmat(seg_id,NULL,0);
    if(mem_ptr==(void*)-1)
        oops("shmat",2);

    semset_id=semget(TIME_SEM_KEY,2,(0666 | IPC_CREAT | IPC_EXCL));
    if(semset_id==-1)
        oops("semget",3);

    set_sem_value(semset_id,0,0);
    set_sem_value(semset_id,1,0);

    signal(SIGINT,cleanup);
    int n;
    time_t now;
    for(n=0;n<60;++n){
        time(&now);
        printf("\tshm_ts2 waiting for lock\n");
        wait_and_lock(semset_id);
        printf("\tshm_ts2 updating memory\n");
        strcpy(mem_ptr,ctime(&now));
        sleep(5);
        release_lock(semset_id);
        printf("\tshm_ts2 released lock\n");
        sleep(1);
    }
    cleanup(0);
}

void cleanup(int n)
{
    shmctl(seg_id,IPC_RMID,NULL);
    semctl(semset_id,0,IPC_RMID,NULL);
}

void set_sem_value(int semset_id,int semnum,int val)
{
    union semun initval;
    initval.val=val;
    if(semctl(semset_id,semnum,SETVAL,initval)==-1)
        oops("semctl",4);
}

void wait_and_lock(int semset_id)
{
    struct sembuf actions[2];
    //阻塞终止条件
    actions[0].sem_num=0;           //sem[0] is n_readers
    actions[0].sem_flg=SEM_UNDO;    //auto cleanup
    actions[0].sem_op=0;            //wait till no readers
    //要执行的动作
    actions[1].sem_num=1;           //sem[1] is n_writers
    actions[1].sem_flg=SEM_UNDO;    //auto cleanup
    actions[1].sem_op=+1;           //incr num writers

    if(semop(semset_id,actions,2)==-1)
        oops("semop:locking",10);
}

void release_lock(int semset_id)
{
    struct sembuf actions[1];
    //要执行的动作
    actions[0].sem_num=1;           //sem[0] is n_writers
    actions[0].sem_flg=SEM_UNDO;    //auto cleanup
    actions[0].sem_op=-1;           //decr writer count

    if(semop(semset_id,actions,1)==-1)
        oops("semop:unlocking",10);
}
```

```cpp
//客户端: shm_tc2.c
#include<stdio.h>
#include<sys/shm.h>
#include<time.h>
#include<sys/types.h>
#include<sys/ipc.h>
#include<sys/sem.h>

#define TIME_MEM_KEY 99
#define TIME_SEM_KEY 9900
#define SEG_SIZE ((size_t)100)
#define oops(m,x) { perror(m); exit(x);}

union semun {int val; struct semid_ds* buf; ushort* array;};

void main()
{
    int seg_id=shmget(TIME_MEM_KEY,SEG_SIZE,0777);
    if(seg_id==-1)
        oops("shmget",1);
    char* mem_ptr=shmat(seg_id,NULL,0);
    if(mem_ptr==(void*)-1)
        oops("shmat",2);

    int semset_id=semget(TIME_SEM_KEY,2,0);
    wait_and_lock(semset_id);

    printf("The time,direct from memory:..%s",mem_ptr);

    release_lock(semset_id);
    shmdt(mem_ptr);     //detach
}

void wait_and_lock(int semset_id)
{
    struct sembuf actions[2];
    //阻塞终止条件
    actions[0].sem_num=1;           //sem[1] is n_writers
    actions[0].sem_flg=SEM_UNDO;    //auto cleanup
    actions[0].sem_op=0;            //wait for 0
    //要执行的动作
    actions[1].sem_num=0;           //sem[0] is n_readers
    actions[1].sem_flg=SEM_UNDO;    //auto cleanup
    actions[1].sem_op=+1;           //incr n_readers

    if(semop(semset_id,actions,2)==-1)
        oops("semop:locking",10);
}

void release_lock(int semset_id)
{
    struct sembuf actions[1];
    actions[0].sem_num=0;
    actions[0].sem_flg=SEM_UNDO;
    actions[0].sem_op=-1;

    if(semop(semset_id,actions,1)==-1)
        oops("semop:unlocking",10);
}
```