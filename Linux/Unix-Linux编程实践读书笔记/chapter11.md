### chapter11 连接到近端或远端的进程：服务器与Socket(套接字)

#### 章节知识总结

Unix提供一个接口(`read`和`write`)来处理来自不同数据源的数据:

1. 磁盘/设备文件：用`open`命令连接，用`read`和`write`传递数据
2. 管道：用`pipe`命令创建，用`fork`共享，用`read`和`write`传递数据
3. Sockets：用`socket`、`listen`和`connect`连接，用`read`和`write`传递数据

`fdopen`与`fopen`类似，返回一个`FILE*`类型的值，不同的是此函数以文件描述符而非文件作为参数，`fdopen`函数通常用于将文件描述符转换为`FILE*`类型
`popen`打开一个指向进程的带缓冲的连接，`popen`的第一个参数是要打开的命令的名称；它可以是任意的`shell`命令。第二个参数可以是"r"或"w"，但决不会是"a"

   * 当完成对`popen`所打开连接的读写后，必须使用`pclose`关闭连接，而不能用`fclose`。进程在产生之后必须等待退出运行，否则它将成为僵尸进程。而`pclose`中调用了`wait`函数来等待进程的结束。
   * 僵尸进程是当子进程比父进程先结束，而父进程又没有回收子进程，释放子进程占用的资源，此时子进程将成为一个僵尸进程（**在UNIX 系统中，一个进程结束了，但是他的父进程没有等待(调用wait / waitpid)他， 那么他将变成一个僵尸进程**）。如果父进程先退出，子进程被init接管，子进程退出后init会回收其占用的相关资源

使用`popen`的一个小demo如下:

```cpp
#include<stdio.h>

void main()
{
    FILE * fp;
    fp=popen("who|sort","r");
    char buf[100];
    int i=0;
    while(fgets(buf,100,fp)!=NULL)
        printf("%3d %s",i++,buf);
    pclose(fp);
}
```

管道只能连接相同的进程（相同父进程），也只能连接同一台主机上的进程。Unix提供了另外一种进程间的通信机制`socket`.

运行于因特网上的服务器其实是某台计算机上运行的一个进程。这里计算机被称为`主机`。机器通常被指定一个名字如sales.xyzcorp.com，这被称为该主机的名字。服务器在该主机上拥有一个端口。`主机`和`端口`的组合才标识了一个服务器。

   * Unix中，在文件`/etc/services`中定义了众所周知服务端口号的列表

`协议`是服务器和客户之间交互的规则。

客户/服务器模式是因特网上经典的一个模型。其中服务器端设计包含以下六个步骤:

1. 向内核申请一个socket(使用系统调用`socket`)：`socket`是产生呼叫和接收呼叫的地方。
2. 绑定地址到socket上，地址包括主机、端口(使用系统调用`bind`):`bind`调用把一个地址分配给socket,其中地址由主机和端口组成，端口号是一个16位的数值。
3. 在socket上，允许接入呼叫并设置队列长度(使用系统调用`listen`):`listen`调用的第二个参数可以指定接收队列的长度。
4. 等待/接收呼叫(使用系统调用`accept`):`accept`调用阻塞当前进程，一直到指定socket上的接入连接被建立起来，**然后accept将返回文件描述符，并用该文件描述符来进行读写操作**。
5. 传输数据(使用Unix中的I/O系统调用):`accept`调用所返回的文件描述符是一个普通文件的描述符，对其的操作和普通文件没有两样。
6. 关闭连接（使用系统调用`close`关闭）：`accpet`所返回的文件描述符可以由标准的系统调用`close`关闭。

客户端设计包含以下四个步骤:

1. 向内核申请一个socket(使用系统调用`socket`)
2. 与服务器相连（使用系统调用`connect`）:`connect`系统调用的作用实际上与打电话类似。当`connect`连接成功时，`sockid`变成一个合格文件描述符，可以通过`sockid`来进行读写操作
3. (and 4.) 传输数据和挂断：在成功连接后，进程可以从该文件描述符`sockid`读写数据。读取完毕后，客户端关闭文件描述符之后退出，若客户端退出而未关闭文件描述符，内核将完成关闭文件描述符的任务

很多服务器程序都是以`d`结尾，如`httpd`、`inetd`等，这里的`d`表示精灵`daemon`的意思（精灵就是一个为他人提供服务的帮助者，它随时等待去帮助别人）

#### 系统调用

| | socket |
| :----: | :----: |
| 用途 | 建立一个socket |
| 头文件 | #include<sys/types.h> #include<sys/socket.h> |
| 函数原型 | sockid=socket(int domain,int type,int protocal) |
| 参数 | domain: 通信域(`PF_INET`用于Internet socket)；type:socket的类型。SOCK_STREAM跟管道类似 ；protocal:协议socket中所用的协议，默认为0 |
| 返回值 | -1:遇到错误; sockid:成功返回 |

socket调用创建一个通信端点并返回一个标识符。有很多类型的通信系统，每个被称为一个通信域。Internet本身就是一个域。在后面会看到Unix内核是另一个域。
socket函数中最后的参数`protocol`指的是内核中网络代码所使用的协议，并不是客户端和服务端之间的协议。一个为0的值代表选择标准的协议。

| | socket |
| :----: | :----: |
| 用途 | 绑定一个地址到socket |
| 头文件 | #include<sys/types.h> #include<sys/socket.h> |
| 函数原型 | result=bind(int sockid,struct sockaddr* addrp,socklen_t addrlen) |
| 参数 | sockid:socket的id; addrp:指向包含地址结构的指针；addrlen:地址长度 |
| 返回值 | -1:遇到错误；0：成功 |

| | listen |
| :----: | :----: |
| 用途 | 监听socket上的连接 |
| 头文件 | #include<sys/socket.h> |
| 函数原型 | result=listen(int sockid,int qsize) |
| 参数 | sockid:接收请求的sockid; qsize:允许接入连接的数目 |
| 返回值 | -1:遇到错误；0：成功 |

| | accept |
| :----: | :----: |
| 用途 | 接受socket上的一个连接 |
| 头文件 | #include<sys/types.h> #include<sys/socket.h> |
| 函数原型 | fd=accept(int sockid,struct sockaddr* callerid,socklen_t* addrlenp) |
| 参数 | sockid:接受该socket上的呼叫；callerid:指向呼叫者地址结构的指针；addrlenp:指向呼叫者地址结构长度的指针 |
| 返回值 | -1:遇到错误；fd:用于读写的文件描述符 |

| | connect |
| :----: | :----: |
| 用途 | 连接socket |
| 头文件 | #include<sys/types.h> #include<sys/socket.h> |
| 函数原型 | result=connect(int sockid,struct sockaddr* serv_addrp, socklen_t addrlen) |
| 参数 | sockid: 用于建立连接的socket; serv_addrp:指向服务器地址结构的指针； addrlen:指向服务器地址结构的长度 |
| 返回值 | -1:遇到错误;0:成功 |

#### rlsd/rls例子

`rls`获取服务器端的文件，`rlsd`通过`ls`命令提供服务，其实现如下:

```cpp
//rlsd.c

#include<stdio.h>
#include<unistd.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<netdb.h>
#include<time.h>
#include<string.h>


#define PORTNUM 15000   // 端口号
#define HOSTLEN 256
#define oops(msg)  { perror(msg); exit(1);}

void sanitize(char*);

int main(int ac,char* av[])
{
    //step1: ask kernel for a socket
    int sock_id=socket(PF_INET,SOCK_STREAM,0);
    if(sock_id==-1)
        oops("socket\n");

    //step2: bind address to socket.Address is host,port
    struct sockaddr_in addr;
    bzero(&addr, sizeof(addr));
    char hostname[HOSTLEN];
    gethostname(hostname,HOSTLEN);
    struct hostent* hp=gethostbyname(hostname);
    if(hp==NULL)
        oops("gethostbyname\n");
    bcopy(hp->h_addr,(struct sockaddr*)&addr.sin_addr,hp->h_length);
    addr.sin_port=htons(PORTNUM);
    addr.sin_family=AF_INET;
    if(bind(sock_id,(struct sockaddr*)&addr,sizeof(addr))!=0)
        oops("bind\n");

    //step3: allow incoming calls with Qsize=1 on socket
    if(listen(sock_id,1)!=0)
        oops("listen\n");


    //main loop: accept(),write(),close()
    while(1){
        int sock_fd=accept(sock_id,NULL,NULL);
        if(sock_fd==-1)
            oops("accept\n");
        FILE *sock_fpi,*sock_fpo;
        if((sock_fpi=fdopen(sock_fd,"r"))==NULL)
            oops("fdopen reading\n");

        char dirname[BUFSIZ];
        if(fgets(dirname,BUFSIZ-5,sock_fpi)==NULL)
            oops("reading dirname\n");

        //dirname检查
        sanitize(dirname);

        if((sock_fpo=fdopen(sock_fd,"w"))==NULL)
            oops("fdopen writing\n");
        char command[BUFSIZ];
        sprintf(command,"ls %s",dirname);
        FILE* pipe_fp;
        if((pipe_fp=popen(command,"r"))==NULL)
            oops("popen\n");
        int c;
        while((c=getc(pipe_fp))!=EOF)
            putc(c,sock_fpo);
        pclose(pipe_fp);
        fclose(sock_fpo);
        fclose(sock_fpi);
    }
}

void sanitize(char* str)
{
    char* src,*dest;
    for(src=dest=str;*src;src++)
        if(*src=='/' || isalnum(*src))
            *dest++=*src;
    *dest='\0';
}

```

```cpp
//rls.c

#include<stdio.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<netdb.h>


#define oops(msg) { write(1,msg,256); exit(1);}
#define PORTNUM 15000   // 端口号

void main(int ac,char* av[])
{
    //step1: Get a socket;
    int sock_id=socket(AF_INET, SOCK_STREAM, 0);
    if(sock_id==-1)
        oops("socket");

    //step2: Connect to server
    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(server_addr));


    struct hostent* hp=gethostbyname(av[1]);
    if(hp==NULL)
        oops(av[1]);
    bcopy(hp->h_addr,(struct sockaddr*)&server_addr.sin_addr,hp->h_length);
    server_addr.sin_port=htons(PORTNUM);
    server_addr.sin_family=AF_INET;

    if(connect(sock_id,(struct sockaddr*)&server_addr,sizeof(server_addr))!=0)
        oops("connect\n");

    //step3: send directory name, then read back results
    if((write(sock_id,av[2],strlen(av[2])))==-1)
        oops("write\n");
    if(write(sock_id,"\n",1)==-1)
        oops("write\n");
    char buffer[BUFSIZ];
    int n_read;
    while((n_read=read(sock_id,buffer,BUFSIZ))>0){
        if(write(1,buffer,n_read)!=n_read)
            oops("write");
    }
    close(sock_id);
}
```