[toc]

### chapter16 网络IPC:套接字

#### 套接字描述符

为创建一个套接字，调用socket函数

```cpp
/*
domain: 通信域
type: 套接字类型
protocol: 协议
*/
int socket(int domain,int type,int protocol);   //若成功，返回文件(套接字)描述符
```

套接字通信域分为:

|域|描述|
|:---:|:---:|
|AF_INET| IPv4因特网域|
|AF_INET6| IPv6因特网域 |
|AF_UNIX| UNIX域 |
|AF_UPSPEC| 未指定 |

套接字类型分为:
|类型|描述|
|:---:|:---:|
|SOCK_DGRAM|固定长度的、无连接的、不可靠的报文传递|
|SOCK_RAM|IP协议的数据报接口|
|SOCK_SEQPACKET|固定长度的、有序的、可靠的、面向连接的报文传递|
|SOCK_STREAM|有序的、可靠的、双向的、面向连接的字节流|

对于数据报(SOCK_DGRAM)接口，两个对等进程之间通信时不需要逻辑连接。只需要向对等进程所使用的套接字送出一个报文。字节流(SOCK_STREAM)要求在交换数据之前，在本地套接字和通信的对等进程的套接字之间建立一个逻辑连接。

SOCK_RAW套接字提供一个数据报接口，用于直接访问下面的网络层(即因特网域中的IP层).使用这个接口时，应用程序负责构建自己的协议头部，这是因为传输协议(如TCP何UDP)被绕过了。当创建一个原始套接字时，需要有超级用户特权，这样可以防止恶意引用程序绕过内建安全机制来创建报文。

协议类型分为:
|协议|描述|
|:---:|:---:|
|IPPROTO_IP|IPv4网络协议|
|IPPROTO_IPV6|IPv6网络协议|
|IPPROTO_ICMP|因特网控制报文协议|
|IPPROTO_RAW|原始IP数据包协议|
|IPPROTO_TCP|传输控制协议|
|IPPROTO_UDP|用户数据报协议|

在AF_INET通信域中，套接字类型SOCK_STREAM的默认协议是传输控制协议(TCP)。在AF_INET通信域中，套接字类型SOCK_DGRAM的默认协议是UDP。

调用socket与调用open相类似。在两种情况下，均可获得用于I/O的文件描述符。当不再需要该文件描述符时，调用close来关闭对文件或套接字的访问，并且释放该描述符以便重新使用。

#### 寻址

在套接字通信过程中，通过进程标识来确定目标通信进程。进程标识由两部分组成，一部分是**计算机的网路地址，它可以帮助标识网络上我们想与之通信的计算机**；另一部分是该**计算机上用端口号表示的服务，它可以帮助标识特定的进程**。


在不同的计算机上进行通信时，需要考虑字节序，不同处理器的字节序有可能不同。在Unix中，网路协议指定了字节序（即网络字节序），因此异构计算机系统能够交换协议信息而不会被字节序所混淆。

TCP/IP协议栈使用**大端字节序**。对于TCP/Ip地址用网络字节序来表示，所以应用程序有时需要在处理器的字节序与网络字节序之间转换它们。(相关函数如下)

```cpp
// h表示“主机”字节序，n表示“网络”字节序。l表示"长"整数，s表示"短"整数
uint32_t htonl(uint32_t host32);
uint16_t htons(uint16_t host16);
uint32_t ntohl(uint32_t netint32);
uint16_t ntohs(uint16_t netint16);
```

一个地址标识一个特定通信域的套接字端点，地址格式与这个特定的通信域相关。为使不同格式地址能够传入套接字函数，地址会被强制转换成一个通用的地址结构sockaddr;

```cpp
struct sockaddr{
    sa_family_t sa_family;      /*address family*/
    char        sa_data[];      /*variable-langth address*/
    //...
};
```

在Linux中，地址用sockaddr_in定义

```cpp
struct sockaddr_in{
    sa_family_t sin_family;     /*address family*/
    in_port_t   sin_port;       /*port number*/
    struct in6_addr sin6_addr;  /*IPv4 address*/
    unsigned char   sin_zero[8];/*filter*/
};
```

不同系统中地址的定义可能不同，在使用的时候，它们均被强制转换成sockaddr结构输入到套接字例程中


对于服务器，需要给一个接受客户端请求的服务器套接字关联上一个众所周知的地址，使用bind函数来关联地址和套接字。

```cpp
int bind(int sockfd,const struct sockaddr* addr,socklen_t len);
```

对于使用的地址有以下一些限制:

* 在进程正在运行的计算机上，指定的地址必须有效；不能指定一个其他机器的地址；
* 地址必须和创建套接字时的地址族所支持的格式相匹配;
* 地址中的端口号必须不小于1024,除非该进程具有相应的特权(即超级用户);
* 一般只能将一个套接字端点绑定到一个给定地址上，尽管有些协议允许多重绑定;

#### 建立连接

要处理一个面向连接的网络服务，那么在考试交换数据以前，需要在请求服务的进程套接字(服务端)和提供服务的进程套接字(服务器)之间建立一个连接。使用connect函数来建立连接。

```cpp
int connect(int sockfd,const struct sockaddr* addr,socklen_t len);  //若成功，返回0；若出错，返回-1
```

要想一个连接请求成功，要连接的计算机必须是开启的，并且正在运行，服务器必须绑定到一个想与之连接的地址上，并且服务器的等待连接队列要有足够的空间。因此，应用程序必须能够处理connect返回的错误，这些错误可能是由一些瞬时条件引起的。

```cpp
//指数补偿的重连算法
int connect_retry(int sockfd,const struct sockaddr* addr,socklen_t alen)
{
    int numsec;
    /*
    *   Try to connect with exponential backoff.
    */
    for(numsec=1;numsec<=MAXSLEEP;numsec<<=1){
        if(connect(sockfd,addr,alen)==0)
            return 0;
        if(numsec<=MAXSLEEP/2)
            sleep(numsec);
    }
    return -1;
}
```

服务器调用listen函数来宣告它愿意接受连接请求:

```cpp
//backlog提供一个提示，提示系统该进程所要入队的未完成连接请求数量。其实际值由系统决定。
int listen(int sockfd,int backlog);     //若成功，返回0；若出错，返回-1
```

一旦服务器调用了listen,所用的套接字就能接受连接请求。使用accept函数获得连接请求并建立连接。

```cpp
int accept(int sockfd,struct sockaddr* restrict addr,socklen_t *restrict len);  //若成功，返回文件(套接字)描述符；若出错，返回-1
```

函数accept所返回的文件描述符是套接字描述符，该描述符连接到调用connect的客户端。这个新的套接字描述符和原始套接字（sockfd）具有相同的套接字类型和地址族。传给accept的原始套接字没有关联到这个连接，而是继续保持可用状态并接受其他连接请求。

#### 数据传输

在套接字通信中欧，有3个函数用来发送数据，3个用于接受数据。

```cpp
//发送数据
ssize_t send(int sockfd,const void* buf,size_t nbytes,int flags);
ssize_t sento(int sockfd,const void* buf,size_t nbytes,int flags,const struct sockaddr* destaddr,socklen_t destlen);        //指定发送的目标地址
ssize_t sendmsg(int sockfd,const struct msghdr* msg,int flags);
//接受数据
ssize_t recv(int sockdf,void* buf,size_t nbytes,int flags);
ssize_t recvfrom(int sockfd,void* restrict buf,size_t len,int flags,struct sockaddr* restrict addr,socklen_t *restrict addrlen);    //接受数据并获取发送者的地址
ssize_t recvmsg(int sockfd,struct msghdr* msg,int flags);
```

#### 带外数据

带外数据是一些通信协议所支持的可选功能，与普通数据相比，它允许更高优先级的数据传输。带外数据先行传输，即使传输队列已经有数据。**TCP支持带外数据，但是UDP不支持**。

TCP将带外数据称为紧急数据，TCP仅支持一个字节的紧急数据，但是允许紧急数据在普通数据传递机制数据流之外传输。如果通过套接字安排了信号的产生，那么紧急数据被接受时，会发送SIGURG信号。


