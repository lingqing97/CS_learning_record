### chapter2 用户、文件操作与联机帮助

#### 章节知识总结

`who`命令通过读取系统日志(`UTMP_FILE`文件)的内容显示当前已经登录的用户.

Unix系统把数据存放在普通文件中，可以通过以下系统调用操作文件:

* open(filename,how):`how`为打开方式(`O_RDONLY`,`O_WRONLY`,`O_RDWR`三种方式)
* creat(filename,mode):`mode`为创建的文件的权限，该权限只是给系统的建议，实际权限由系统的`umask`决定
* read(fd,buffer,amt):`amt`为读取的size大小，该函数返回值为实际读取的size大小
* write(fd,buffer,amt):同`read`,该函数返回值为实际读取的size大小
* lseek(fd,distance,base);将文件指针移动到指定位置,`base`为参考坐标,`distance`为偏移量
* close(fd):关闭文件

进程对文件的读/写都要通过文件描述符，文件描述符表示文件和进程之间的连接.

  * 如果同时打开好几个文件，它们所对应的文件描述符是不同的；如果将一个文件打开多次，对应的文件描述符也是不同的。

**每次系统调用都会导致用户模式和内核模式的切换**以及执行内核代码，所以减少程序中的系统调用发生的次数可以提高程序的运行效率。

  * 当工作在内核模式时，程序可以直接访问磁盘、终端、打印机等设备，还可以访问全部的内存空间；而在用户模式，程序不能直接访问设备，也只能访问特定部分的内存空间。

程序可以通过缓冲技术来减少系统调用的次数，仅当写缓冲区满或读缓冲区空时才调用内核服务。(Unix内核中采用了缓冲技术来减少访问磁盘I/O的次数)

内核运用缓冲技术导致的结果:

* 提高磁盘I/O效率
* 优化磁盘的写操作
* 需要及时地将缓冲数据写入磁盘（系统异常断点等情况可能会导致缓冲中的数据不能及时写回磁盘）

当系统调用出错时会把全局变量`errno`的值设为相应的错误代码，返回返回-1,程序可以通过检测`errno`来确定错误的类型，并采取相应的措施。(在`<errno.h>`头文件中有相应的说明)

#### cp指令实现

`cp`指令的简易实现如下：

```cpp
/*
    cp指令简易实现
*/
#include<stdio.h>
#include<fcntl.h>    //for open() and creat()
#include<unistd.h>   //for close() and read()

#define BUFSIZE 4096    //声明缓冲区大小
#define FMODE 0644      //声明创建的文件权限

//声明打印错误信息的函数
void oop(char* ,char*);

int main(int ac,char* av[]){

    //参数数量检查
    if(ac!=3){
        fprintf(stderr,"usage: %s source destination\n",*av);
        exit(1);
    }

    //判断源文件和目标文件是否相同
    if(strcmp(av[1],av[2])==0){
        fprintf(stderr,"cp: %s and %s are the same file. \n",av[1],av[2]);
        exit(1);
    }

    //打开源文件
    int source_fp;
    if((source_fp=open(av[1],O_RDONLY))==-1){
        oop("open file error",av[1]);
    }

    //创建目标文件
    int taget_fp;
    if((taget_fp=creat(av[2],FMODE))==-1){
        oop("creat file error",av[2]);
    }

    //复制源文件到目标文件
    char buf[BUFSIZE];
    int n_char;
    while((n_char=read(source_fp,&buf,BUFSIZE))>0){
        if((write(taget_fp,&buf,n_char))!=n_char)
            oop("write file error",av[2]);
    }

    //关闭文件
    if(close(source_fp)==-1||close(taget_fp)==-1){
        oop("close file error",av[0]);
    }

    return 0;
}

void oop(char* error,char* filename){
    fprintf(stderr,"usage: %s",error);
    perror(filename);
    exit(1);
}
```

#### who指令实现

`who`指令的简易实现如下：

```cpp
/*
    who指令简易实现
*/
#include<stdio.h>
#include<fcntl.h>    //for open() and creat()
#include<unistd.h>   //for read() and write()
#include<time.h>     //for ctime()
#include<utmp.h>     //for struct utmp

#define BUF_NUM 16   //定义缓冲区数量
#define BUF_SIZE (sizeof(struct utmp))  //定义缓冲区单位大小
#define NULLUTP ((struct utmp*)NULL)

#define SHOWHOST
#define ACTIVE_ONLY

//函数声明
void show_time(long);
void show_info(struct utmp*);

static char utmpbuf[BUF_NUM*BUF_SIZE];  //缓冲区大小
static int  num_recs;                   //缓冲区总存量
static int  cur_rec;                    //当前已使用缓冲区个数
static int  fd_utmp=-1;                 //utmp文件的文件描述符

//打开utmp文件
int utmp_open(char* filename){
    fd_utmp=open(filename,O_RDONLY);
    num_recs=cur_rec=0;
    return fd_utmp;
}

//申请更多缓冲区
int utmp_reload(){
    int amt_read;
    amt_read=read(fd_utmp,&utmpbuf,BUF_NUM*BUF_SIZE);
    num_recs=amt_read/BUF_SIZE;
    cur_rec=0;
    return num_recs;
}

//读取下一个数据
struct utmp* utmp_next()
{
    struct utmp* recp;
    if(fd_utmp==-1)
        return NULLUTP;
    //当缓冲区全部用完后，重新申请
    //若申请为0，表示读取utmp完毕
    while(1){
        if(cur_rec==num_recs&&utmp_reload()==0)
            return NULLUTP;
        recp=(struct utmp*)&utmpbuf[cur_rec*BUF_SIZE];
        ++cur_rec;
        #ifdef ACTIVE_ONLY
        if(recp->ut_type==USER_PROCESS)
        #endif
            return recp;
    }
    return NULLUTP;
}

//关闭utmp文件
void utmp_close(){
    if(fd_utmp!=-1)
        close(fd_utmp);
}

int main(){
    if(utmp_open(UTMP_FILE)==-1){
        perror(UTMP_FILE);
        exit(1);
    }
    struct utmp* utbufp;
    while((utbufp=utmp_next())!=(struct utmp*)NULL)
        show_info(utbufp);
    utmp_close();
    return 0;
}

void show_info(struct utmp* utp){
    //为在线的用户信息不打印
    if(utp->ut_type!=USER_PROCESS) return;
    printf("%-8.8s",utp->ut_user);      //the logname
    printf(" ");
    printf("%-8.8s",utp->ut_line);      //the tty
    printf(" ");
    show_time(utp->ut_time);            //the log time
    #ifdef SHOWHOST
    if(utp->ut_host[0]!='\0')
        printf("(%s)",utp->ut_host);    //the host
    #endif
    printf("\n");
}

void show_time(long timeval){
    char *cp;
    cp=ctime(&timeval);
    //cp="Tue Feb 23 09:25"
    printf("%12.16s",cp+4);
}
```