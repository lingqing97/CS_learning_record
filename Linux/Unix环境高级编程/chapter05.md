### chapter05 标准I/O库

#### 理论知识

在前面的第3章中，所有I/O函数都是围绕文件描述符的。当打开一个文件时，即返回一个文件描述符，然后该文件描述符就用于后续的I/O操作。而对于标准I/O库，它们的操作是围绕`流`进行的。当用标准I/O库打开或创建一个文件时，我们已使一个流与一个文件相关联。(可以通过`fileno`获取与其关联的文件描述符)

`流的定向`决定了所读、写的字符是单字节还是多字节的。当一个流最初被创建时，它没有定向，可以通过函数`fwide`设置流的定向。

当通过函数`fopen`打开一个流时，返回一个指向`FILE`对象的指针。该对象指向一个结构，该结构包含了标准的I/O库为管理该流需要的所有信息，包括用于实际I/O的文件描述符、**指向用于该流缓冲区的指针、缓冲区的长度、当前在缓冲区中的字符数**以及出错标志等。

从前面我们知道，文件描述符`STDIN_FILENO`、`STDOUT_FILENO`、`STDERR_FILENO`自动被进程打开，同样在标志I/O中，预定义文件指针`stdin`、`stdout`和`stderr`加以引用。

标志I/O库提供了3种类型的缓冲来减少对`read`和`write`的系统调用:

1. 全缓冲(`_IOFBF`)：在这种情况下，在填满标准I/O缓冲区后才进行实际I/O操作
2. 行缓冲(`_IOLBF`)：在这种情况下，当在输入和输出中遇到换行符时，标准I/O库执行I/O操作
3. 不带缓冲(`_IONBF`)：标准I/O库不对字符进行缓冲存储

术语`冲洗(flush)`有两种含义:在标准I/O库方面,`flush(冲洗)`意味着将缓冲区中的内容写到磁盘上（该缓冲区可能只是部分填满的）；在终端驱动程序方面，`flush(刷清)`表示丢弃已存储在缓冲区中的数据。

很多系统对缓冲的规定如下:

1. 标准错误是不带缓冲的
2. 若是指向终端设备的流，则是行缓冲的；否则是全缓冲的

当使用`fopen`以读和写(`r+`、`w+`或`a+`)类型打开一个文件时，具有下列限制:

1. 如果中间没有`fflush`、`fseek`、`fsetpos`或`rewind`，则在输出的后面不能直接跟随输入
2. 如果中间没有`fseek`、`fsetpos`或`rewind`，或者一个输入操作没有到达文件尾端，则在输入操作之后不能直接跟随输出

一旦打开了流，则可在3种不同类型的`非格式化I/O`中进行选择:

1. 每次一个字符的I/O（典型代表`getc`、`fgetc`、`putc`和`fputc`）:一次读或写一个字符，如果流是带缓冲的，则标准I/O函数处理所有缓冲
2. 每次一行的I/O(典型代表`fgets`和`fputs`):一次读或写一行
3. 直接I/O(典型代表`fread`和`fwrite`):也被称为一次一个对象的I/O、面向记录的I/O或面向结构的I/O

使用`ferror`和`feof`可以打印标准I/O中的错误，在大多数实现中，为每个流在`FILE`对象中维护了两个标志:

1. 出错标志
2. 文件结束标志

`格式化I/O`中，格式化输出由`printf`族函数来处理，格式化输入由`scanf`族函数来处理,在格式化输入和输出中，都可以定义格式说明控制来对输入/输出格式化


标准I/O库中提供了`tmpfile`、`mkstemp`等函数来创建临时文件，其中`mkstemp`创建的临时文件需要自己对它解除链接

#### 函数调用

调用`fileno`获得与文件指针fp关联的文件描述符

```cpp
#include<stdio.h>

int fileno(FILE* fp);
```

使用`fflush`将流所有未写的数据都被传送至内核。

```cpp
#include<stdio.h>

int fflush(FILE* fp);
```

使用`fopen`以`r`、`w`等`type`打开路径名为`pathname`的文件

调用`fclose`关闭一个打开的流。注意，当一个进程正常终止时(直接调用exit函数，或从main函数返回)，则**所有带未写缓冲数据的标准I/O流都被冲洗，所有打开的标准I/O流都被关闭**。

```cpp
#include<stdio.h>

FILE* fopen(const char* restrict pathname ,const char* restrict type);

FILE* fdopen(int fd,const char* type);      //取一个已有的文件描述符，常用于由创建管道和网络通信管道函数返回的描述符

int fclose(FILE* fp);
```

在标准I/O中打印错误的通用函数如下:

```cpp
#include<stdio.h>

int ferror(FILE* fp);
int feof(FILE* fp);

void clearerr(FILE* fp);    //清除出错标志和文件结束标志
```

常用非格式化I/O如下:

```cpp
#include<stdio.h>

//每次一个字符的I/O
int getc(FILE* fp);
int fgetc(FILE* fp);        //与getc的唯一不同是不能实现为宏
int getchar(void);          //等价于getc(stdin)

int putc(int c,FILE* fp);
int fputc(int c,FILE* fp);
int putchar(int c);


//每次一行I/O

char* fgets(char* restrict buf,int n,FILE* restrict fp);

int fputs(const char* restrict str,FILE* restrict fp);

//直接I/O
//常用于二进制的I/O操作

size_t fread(void* restrict ptr,size_t size,size_t nobj,FILE* restrict fp);
size_t fwrite(const void* restrict ptr,size_t size,size_t nobj,FILE* restrict fp);

```

格式化输出和格式化输入函数如下:

```cpp
#include<stdio.h>

//格式化输出
int printf(const char* restrict format,...);    //输出到标准输出
int fprintf(FILE* restrict fp,const char* restrict format,...); //输出到文件指针fp
int dprintf(int fd,const char* restrict format,...); //输出到文件描述符fp
int sprintf(char* restrict buf,const char* restrict format,...); // 输出到缓冲区buf

//格式化输入
int scanf(const char* restrict format,...); //从标准输入获取输入
int fscanf(FILE* restrict fd,const char* restrict format,...); //从文件指针fp中获取输入
int sscanf(const char* restrict buf,const char* restrict format,...); //从缓冲区buf中获取输入
```

使用`tmpnam`和`tmpfile`创建临时文件的实例:

```cpp
#include<stdio.h>
#include<unistd.h>

#define MAXLINE 1024

int main(void)
{
    char name[L_tmpnam],line[MAXLINE];
    FILE* fp;

    printf("%s\n",tmpnam(NULL));

    tmpnam(name);
    printf("%s\n",name);

    if((fp=tmpfile())==NULL)
    {
        fprintf(stderr,"tmpfile error\n");
        exit(1);
    }
    fputs("one line of output\n",fp);
    rewind(fp);
    if(fgets(line,sizeof(line),fp)==NULL)
    {
        fprintf(stderr,"fgets error\n");
        exit(2);
    }
    fputs(line,stdout);
    exit(0);
}
```

使用`mkstemp`创建临时文件的实例:

```cpp
#include<stdio.h>
#include<unistd.h>
#include<sys/errno.h>
#include<sys/stat.h>

void make_temp(char* template);

int main()
{
    char good_template[]="/tmp/dirXXXXXX";
    char *bad_template="/tmp/dirXXXXXX";        //位于只读段

    printf("trying to create first temp file...\n");
    make_temp(good_template);
    printf("trying to create second temp file...\n");
    make_temp(bad_template);        //报错: Segmentation fault, 因为bad_template不可写入
    exit(0);
}

void make_temp(char* template)
{
    int fd;
    struct stat sbuf;

    if((fd=mkstemp(template))<0)        //mkstemp会修改template字符串，所以template所指字符串要可写
    {
        fprintf(stderr,"mkstemp error\n");
        exit(1);
    }
    printf("temp name=%s\n",template);
    close(fd);
    if(stat(template,&sbuf)<0){
        if(errno == ENOENT)
            printf("file doesn't exist\n");
        else{
            fprintf(stderr,"stat failed\n");
            exit(2);
        }
    }
    else{
        printf("file exists\n");
        unlink(template);       //mkstemp创建的文件不会自动删除，要自己对它解除链接
    }
}
```