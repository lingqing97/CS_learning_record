### chapter13 基于数据报的编程:编写许可证服务器

#### 章节知识总结

流socket传送数据就像电话网中传送声音一样，客户先建立连接，然后使用该连接进行单向、双向或类似管道的字节流传送。

数据报通信则与从一个邮箱到另一个邮箱发送包裹类似。客户不必建立连接，只要想特定的地址发送消息，而服务器进程在该进程接受消息。

流socket使用的网络协议叫`TCP`即传输控制挟制(`Transmission Control Protocol`)。数据报socket叫`UDP`即用户数据协议(`User Datagram Protocol`)。

`TCP`协议与`UDP`协议的区别如下所示:

| TCP | UDP |
| :----: | :----: |
| 分片/重组 | 否 |
| 排序 | 否 |
| 可靠的 | 可能未到达 |
| 连接的 | 多个发送者，不必建立连接 |

Web服务器和e-mail信息可能是大的文件，这些字节流必须完全和排序到达目的地，所以选择TCP协议较好，而UDP对于允许丢失帧的声音和视频流是较好的选择。

数据报socket可以被理解成一个内部有数据的盒子，发送者给出目的地socket的地址。网络将数据从发送者发送到目的socket.接受进程从该socket中读取数据，程序使用`sendto`发送数据和`recvfrom`来读取数据。

使用数据报进行通信的例子如下所示,`dgrecv.c`使用命令行传过来的端口号建立socket,接受和打印从客户端发来的数据报;`dgsend.c`创建一个socket,然后用它发送消息到以命令行参数传入的特定的主机和端口号。

```cpp
//辅助函数 dgram.c
#include<stdio.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<string.h>
#include<netdb.h>
#include<arpa/inet.h>

#define oops(msg) { perror(msg); exit(1);}

int make_server_socket(int portnum)
{
    int sock=socket(AF_INET,SOCK_DGRAM,0);
    if(sock==-1) oops("socket");
    struct sockaddr_in addr;
    char hostname[BUFSIZ];
    gethostname(hostname,BUFSIZ);
    make_address(hostname,portnum,&addr);
    if(bind(sock,(struct sockaddr*)&addr,sizeof(addr))!=0)
        oops("bind");
    return sock;
}

int make_client_socket()
{
    return socket(AF_INET,SOCK_DGRAM,0);
}

void make_address(char* hostname,int portnum,struct sockaddr_in* addr)
{
    bzero(addr,sizeof(struct sockaddr_in));
    struct hostent* hp=gethostbyname(hostname);
    if(hp==NULL) oops("gethostbyname");
    bcopy(hp->h_addr,(void*)&addr->sin_addr,hp->h_length);
    addr->sin_port=htons(portnum);
    addr->sin_family=AF_INET;
}

void got_internet_address(char* host,int len,int* portp, struct sockaddr_in* addrp)
{
    strncpy(host,inet_ntoa(addrp->sin_addr),len);
    *portp=ntohs(addrp->sin_port);
}
```

```cpp
//服务端 dgrecv.c
#include<stdio.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>

#define oope(msg,x) { perror(msg); exit(x); }

int make_server_socket(int portnum);
void say_who_called(struct sockaddr_in*);
void got_internet_address(char*,int,int*,struct sockaddr_in*);

int main(int ac,char* av[])
{
    int port;
    if((ac==1 || ((port=atoi(av[1]))<0))){
        fprintf(stderr,"usage: parameter format error");
        exit(1);
    }
    int sock=make_server_socket(port);
    struct sockaddr_in addr;
    char buf[BUFSIZ];
    int msglen;
    int addrlen=sizeof(addr);
    while((msglen=recvfrom(sock,buf,BUFSIZ,0,&addr,&addrlen))>0){
        printf("wait...");
        buf[msglen]='\0';
        printf("dgrecv: got a message:%s \n",buf);
        say_who_called(&addr);
        reply_to_sender(sock,buf,&addr,addrlen);
    }
    return 0;
}

void say_who_called(struct sockaddr_in* addrp)
{
    char host[BUFSIZ];
    int port;
    got_internet_address(host,BUFSIZ,&port,addrp);
    printf("from: %s:%d\n",host,port);
}

void reply_to_sender(int sock,char* buf,struct sockaddr_in* addrp,socklen_t addrlen)
{
    char reply[BUFSIZ+BUFSIZ];
    sprintf(reply,"Thanks for you %d char message\n",strlen(buf));
    sendto(sock,reply,strlen(reply),0,addrp,addrlen);
}
```

```cpp
//客户端 dgsend.c
#include<stdio.h>
#include<sys/socket.h>
#include<sys/types.h>
#include<netdb.h>
#include<netinet/in.h>

#define oops(msg,x) { perror(msg); exit(x);}

int make_client_socket();
void make_address(char* hostname,int portnum,struct sockaddr_in* addr);
//void got_internet_address(char* host,int len,int* portp, struct sockaddr_in* addrp);

int main(int ac,char* av[])
{
    if(ac!=4){
        fprintf(stderr,"usage: parameter format error\n");
        exit(1);
    }
    int sock=make_client_socket();
    struct sockaddr_in addr;
    make_address(av[1],atoi(av[2]),&addr);
    int port=atoi(av[2]);
    //got_internet_address(av[1],strlen(av[1]),&port,&addr);
    if(sendto(sock,av[3],strlen(av[3]),0,&addr,sizeof(addr))==-1)
        oops("sendto error",2);
    char message[BUFSIZ+BUFSIZ];
    int addrlen=sizeof(addr);
    int msglen=recvfrom(sock,message,BUFSIZ+BUFSIZ,0,&addr, &addrlen);
    if(msglen<=0)
        return 0;
    printf("%s\n",message);
    return 0;
}
```

Unix中有两种`socket`地址：Internet地址和本地地址；`Internet`地址包含主机ID和端口号。本地地址通常叫做`Unix`域地址，它是一个文件名，没有主机和端口号。通过`read`和`sendto`来收发数据。

这里举一个日志服务器的例子来说明`Unix域socket编程`.日志服务器是一个抄写员；客户发送信息给服务器，服务器将这些信息保存到只有自己可以修改的文件中。

```cpp
//服务端: logfiled.c

#include<stdio.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<sys/un.h>
#include<time.h>

#define MSGLEN 512
#define oops(m,x) { perror(m);exit(x);}
#define SOCKNAME "/tmp/logfilesock"

int main(int ac,char* av[])
{
    char sockname[]=SOCKNAME;
    struct sockaddr_un addr;
    addr.sun_family = AF_UNIX;
    strcpy(addr.sun_path, sockname);
    int addrlen=strlen(sockname)+sizeof(addr.sun_family);

    int sock=socket(PF_UNIX,SOCK_DGRAM, 0);
    if(sock==-1)
        oops("socket",2);

    //bind
    if(bind(sock,(struct sockaddr*)&addr,addrlen)==-1)
        oops("bind",3);

    int msgnum=0;
    while(1)
    {
        char msg[MSGLEN];
        int l=read(sock,msg,MSGLEN);
        msg[l]='\0';
        time_t now;
        time(&now);
        char* timestr=ctime(&now);
        timestr[strlen(timestr)-1]='\0';

        printf("[%5d] %s %s \n",msgnum++,timestr,msg);
        fflush(stdout);
    }
}
```

```cpp
//客户端: logfilec.c

#include<stdio.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<sys/un.h>

#define SOCKEY "/tmp/logfilesock"
#define oops(m,x) { perror(m); exit(x);}

void main(int ac,char* av[])
{
    if(ac!=2)
    {
        fprintf(stderr,"usage:logfilec 'message'\n");
        exit(1);
    }

    int sock=socket(PF_UNIX,SOCK_DGRAM,0);
    if(sock==-1)
        oops("socket",2);

    struct sockaddr_un addr;
    char sockname[]=SOCKEY;
    addr.sun_family=AF_UNIX;
    strcpy(addr.sun_path,sockname);
    int addrlen=strlen(addr.sun_path)+sizeof(addr.sun_family);

    char* msg=av[1];
    if(sendto(sock,msg,strlen(msg),0,&addr,addrlen)==-1)
        oops("sendto",3);
}
```

`socket`对于进程间的数据通信是强大的，这里进行一个小结

| | 域 | |
| :----: | :----: | :----: |
| socket | PF_INET | PF_UNIX |
| SOCK_STREAM | 连接的，跨机器 | 连接的，本地 |
| SOCK_DGRAM | 数据报，跨机器 | 数据报，本地 |

#### 系统调用


| | sendto |
| :----: | :----: |
| 用途 | 从socket发送消息 |
| 头文件 | #include<sys/types.h> #include<sys/socket.h> |
| 函数原型 | nchars=sendto(int socket,const void* msg,size_t len,int flags,const struct sockaddr* dest,socklen_t dest_len); |
| 参数 | socket: socket_id; msg:发送的字符类型的数组; len:发送的字节数;  flags: 比特的集合，设置发送属性，0表示普通；dest:指向远端socket地址的指针；dest_len:地址长度 |
| 返回值 | -1:遇到错误；nchars:发送的字符数 |


| | recvfrom |
| :----: | :----: |
| 用途 | 从socket接受消息 |
| 头文件 | #include<sys/types.h> #include<sys/socket.h>|
| 函数原型 | nchars=recvfrom(int socket,const void* msg,size_t len,int flags,const struct sockaddr* sender,socklen_t* sender_len); |
| 参数 | socket: socket_id; msg:发送的字符类型的数组；len:发送的字节数； flags:表示接收属性的比特的集合，0表示普通；sender:指向远端socket的地址的指针；sender_len:地址长度 |
| 返回值 | -1:遇到错误；nchars:接收的字符数 |



