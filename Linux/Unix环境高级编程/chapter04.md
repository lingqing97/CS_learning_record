### chapter04 文件和目录

#### 函数stat,fstat,fstatat和lstat

通过`stat`,`fstat`,`fstatat`和`stat`四个函数可以返回文件的详细信息:

```cpp
#include<sys/stat.h>

int stat(const char* restrict pathname, struct stat* restrict buf);

int fstat(int fd,struct stat* buf);

int lstat(const char* restrict pathname,struct stat* restrict buf);

int fstatst(int fd,const char* restrict pathname,struct stat* restrict buf);
```

`lstat`函数类似于`stat`,但是当命名的文件是一个符号链接时，`lstat`返回给符号链接的有关信息，而不是由该符号链接引用的文件的信息.

> `fstat`函数传入文件描述符，在Unix中很多以`f`开头的函数相比于不是`f`开头的函数的区别就是传入的参数是不是文件描述符`fd`,比如`fchmod`，`fchown`,`ftruncate`等

上面四个函数通过填充由`buf`指向的结构来返回文件信息，该结构的实际定义可能随具体实现有所不同，但其基本形式是:

(***)stat结构

```cpp
struct stat{
    mode_t      st_mode;        //记录文件类型+读写权限
    ino_t       st_ino;         //记录i节点编号
    dev_t       st_dev;         //记录设备号
    dev_t       st_rdev;        //记录实际设备号，只有当文件是块设备或字符设备时才有
    nlink_t     st_nlink;       //指向i节点的链接数
    uid_t       st_uid;         //用户ID
    gid_t       std_gid;        //组ID
    off_t       st_size;        //size in bytes, for regular files
    struct timespec st_atime;   //文件最后访问时间
    struct timespec st_mtime;   //文件最后修改时间
    struct timespce st_ctime;   //文件最后状态更新时间(记录在i节点上)
    blksize_t   st_blksize;     //best I/O block size
    blkcnt_t    st_blocks;      //number of disk blocks allocated
};
```

其中`timespec`结构类型按照秒和纳秒定义了时间，至少包括下面两个字段:

```cpp
time_t tv_sec;
long tv_nsec;
```

#### 文件类型

(***)UNIX中的文件类型包括以下几种:

1. 普通文件(regular file)
2. 目录文件(directory file)
3. 块特殊文件(block specila file)
4. 字符特殊文件(character special file)
5. FIFO(也被称为命名通道)
6. 套接字(socket)
7. 符号链接

##### 实例：通过定义的宏判断文件类型

```cpp
#include<stdio.h>
#include<sys/stat.h>

#define oops(m,x) { perror(m); exit(x); }

int main(int ac,char* av[])
{
    int i;
    struct stat buf;
    char *ptr;
    for(i=1;i<ac;++i)
    {
        if(lstat(av[i], &buf)<0)
            oops("lstat",1);
        if(S_ISREG(buf.st_mode))
            ptr="regular";
        else if(S_ISDIR(buf.st_mode))
            ptr="directory";
        else if(S_ISCHR(buf.st_mode))
            ptr="char";
        else if(S_ISBLK(buf.st_mode))
            ptr="block";
        else if(S_ISFIFO(buf.st_mode))
            ptr="FIFO";
        else if(S_ISLNK(buf.st_mode))
            ptr="link";
        else if(S_ISSOCK(buf.st_mode))
            ptr="socket";
        else
            ptr="unkown";
        printf("%s\n",ptr);
    }
    return 0;
}
```

#### 设置用户ID和设置组ID

与一个进程相关联的ID有6个或更多:

![avatar](../image/../../image/unix_用户ID_组ID.jpg)

通常，有效用户ID等于实际用户ID，有效组ID等于实际组ID。当执行一个程序文件时，进程的有效用户ID通常就实际用户ID，有效组ID通常就是实际组ID.

(***) 但是可以在文件模式字(st_mode)中设置一个特殊标志，其含义是”执行此文件时，将进程的有效用户ID设置为文件所有者的用户ID(st_uid)“。与此类似，在文件模式字中可以设置另一位，它将执行此文件的进程的有效组ID设置文件的组所有者ID(st_gid)。在文件模式字中的这两位被称为`设置用户ID(set-user-ID)位`和`设置组ID(set-group-ID)位`.


#### 文件访问权限

所有文件类型(目录、字符特别文件等)都有访问权限(access permission)。很多人认为只要普通文件有访问权限，这是一种误解。

每个文件有9个访问权限位，可将它们分为3类:

![avatar](../image/../../image/unix_9个访问权限位.jpg)

(***)进程每次打开、创建或删除一个文件时，内核就进行文件访问权限测试，内核进行的测试具体如下:

1. 若进程的有效用户是0(超级用户),则允许访问。
2. 若进程的有效用户ID等于文件的所有者(也就是进程拥有此文件)，那么如果所有者适当的访问权限位被设置，则允许访问(比如要对文件进行写操作，则该进程有效用户应该有写权限)
3. 若进程的有效组ID或进程的附属组ID之一等于文件的组ID，那么如果组适当的访问权限位被设置，则允许访问；否则拒绝访问

注意，上述测试顺序执行，即如果进程拥有此文件(第2步),则按用户权限访问批准或拒绝该进程对文件的访问---不查看组访问权限。


#### 新文件和目录的所有权

