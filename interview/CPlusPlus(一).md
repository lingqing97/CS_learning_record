## Day-1

### 问题

> 检查下面代码有什么问题?

```cpp
void GetMemory( char *p )
{
 p = (char *) malloc( 100 );
}
void Test( void )
{
 char *str = NULL;
 GetMemory( str );
 strcpy( str, "hello world" );
 printf( str );
}
```

### 参考答案

错误有:

1. 传入`GetMemory()`函数的形参为字符串指针，在函数内部改变形参的值并不能真正改变传入形参的实际值，所以执行完`GetMemory(str)`后,`str`的值还是`NULL`.
2. 在`GetMemory()`中没有与`malloc`对应的`free`，造成内存泄露.
3. `printf(str)`改为`printf("%s",str)`可以避免`格式化字符串攻击`.

修改后的代码为:

```cpp
void GetMemory(char ** p)
{
    *p=(char*)malloc(100);
    //注意点一：要判断内存申请是否成功
    if(*p==0){
        printf("内存申请失败\n");
        exit(1);
    }
}

void Test(void)
{
    char* str=NULL;
    //注意点二：传入的是指针的指针
    GetMemory(&str);
    strcpy(str,"hello world");
    printf("%s\n",str);
    //注意点三：要对malloc分配的内存进行释放
    free(str);
    //注意点四：free之后,str是野指针，需要将其置为NULL
    str=NULL;
}
```

### 知识点

#### strcpy实现

参考:[strcpy函数的实现](https://www.cnblogs.com/chenyg32/p/3739564.html)

这里使用了C语言库函数`strcpy`，所以有必要对`strcpy`的实现有了解，其一般实现如下:

```cpp
char* strcpy(char* dst,const char* src)
{
    assert (dst!=0 && src!=0);
    char* ret=dst;
    while((*dst++=*src++)!='\0');       /* 注意while循环的写法，不要写成 while(*src!='\0) *dst++=*src++; */
    return ret;
}
```

##### 问题1：src为什么使用`const`修饰

防止修改源字符串.

##### 问题2：空指针检查

注重代码的健壮性.

##### 问题3：返回目标地址

返回dst的原始值使函数能够支持链式表达式.

链式表达式的形式如:

```cpp
int l=strlen(strcpy(strA,strB));

char* strA=strcpy(new char[10],strB);
```

##### 问题4:考虑dst和src内存重叠的情况,strcpy该如何实现

所谓内存重叠，即src未处理的部分被dst给先覆盖了，只有一种情况`dst>src && dst<=src+strlen(src)`

可以使用C库函数`memcpy`自带的内存重叠检测功能进行处理，这里我们自己实现如下:

```cpp
#include<stdio.h>
#include<assert.h>

char* my_memcpy(char* dst,const char* src,int cnt)
{
    assert(dst!=0 && src!=0);
    char* ret=dst;
    if(dst>src && dst<=src+cnt-1) /* 处理内存重叠情况 */
    {
        //printf("case 1\n");
        dst=dst+cnt-1;
        src=src+cnt-1;
        /* 内存重叠时从高地址开始复制 */
        while(cnt--)
            *dst--=*src--;
    }
    else{       /* 正常情况 */
        //printf("case 2\n");
        while(cnt--)
            *dst++=*src++;
    }
    return ret;
}

char* strcpy(char* dst,const char* src)
{
    assert(dst!=0 && src!=0);
    char* ret=my_memcpy(dst,src,strlen(src)+1);
    return ret;
}

//Test
int main(void)
{
    const char* line="hello";
    char str[100];
    //正常情况
    strcpy(str,line);
    printf("%s\n",str);
    //内存重叠
    strcpy(str+1,str);
    printf("%s\n",str);
    return 0;
}
```

> 补充：[面试题之strcpy/strlen/strcat/strcmp的实现](https://songlee24.github.io/2015/03/15/string-operating-function/)

