### chapter06 系统数据文件和信息

最近发现APUE实在是太难”啃“了，打算尝试用一种新的方式看这本书，现忽略一些不重要的函数调用，主要关注理论知识。

#### 重点知识

UNIX系统的正常运行需要使用大量与系统有关的数据文件，比如`口令文件`、`组文件`等

`口令文件`在`POSIZ.1`中也被称为`用户数据库`,`口令文件`是`/etc/passwd`,而且是一个ASCII文件，其中各字段之间用冒号分割，包括`用户名`、`加密口令`（现在普遍不将加密口令放在口令文件中）、`数值用户ID`、`数值组ID`等信息

与口令文件相关的函数如下:

```cpp
#include<pwd.h>

// 获取与登录用户关联的口令文件项
struct passwd* getpwuid(uid_t uid);
struct passwd* getpwnam(const char* name);

// 获取所有的口令文件项
struct passwd* getpwent(void);

//将getpwent()的读写地址指回密码文件开头
void setpwent(void);

//关闭密码文件
void endpwent(void);
```

##### getpwname的简单实现

```cpp
#include<pwd.h>
#include<stddef.h>
#include<string.h>

struct passwd*
getpwnam(const char* name)
{
    struct passwd* ptr;
    setpwent();
    while((ptr=getpwent())!=NULL)
    {
        if(strcmp(name,ptr->pw_name)==0)
            break;
    }
    endpwent();
    return ptr;
}
```

虽然对于一个加密口令，找不到一个算法可以将其反变换到明文口令(明文口令是在Password:提示后键入的口令),但是可以对口令进行猜测，将猜测的口令经单向算法变换成加密形式。所以说加密口令也并不是完全安全的。

为了系统安全性，现在，某些系统将加密口令存放在另一个通常称为`阴影口令(shadow password)`的文件`/etc/shadow`中，该文件至少要包含用户名和加密口令。此外，阴影口令不应是一般用户可以读取的，仅有少数几个程序需要访问加密口令。而有了阴影口令文件后，普通口令文件`/etc/passwd`可由各用户自由读取。

`组文件`在`POSIX.1`中也被称为`组数据库`,`组文件`是`/etc/group`，其中包含`组名`、`数值组ID`等字段。

与组文件相关的函数如下:

```cpp
#include<grp.h>

//获取与当前进程组关联的组文件项
struct group* getgrgid(gid_t gid);
struct group* getgrnam(const char* name);

//获取组文件的所有文件项
struct group* getgrent(void);

void setgrent(void);
void endgrent(void);
```

现在的UNIX系统中，我们不仅可以属于口令文件记录项中组ID所对应的组，也可属于多至16个另外的组。所以这时，文件访问权限检查相应被修改为：不仅将进程的有效组ID与文件的组ID相比较，而且也将所有附属组ID与文件的组ID进行比较。(使用附属组ID的优点是不必再显示地经常更改组)

```cpp
#include<unistd.h>

//获取进程所属用户的所有附属组
int getgroups(int gidsetsize,git_t grouplist[]);    //将获取的所有附属组ID写到grouplist中
```

登录账号记录：`utmp`文件记录当前登录到系统的各个用户；`wtmp`文件跟踪各个登录和注销事件。登录时，`login`程序将登录数据写入到`utmp`文件中，同时也将其添写到`wtmp`文件中。注销时，`init`进程将`utmp`文件中相应的记录擦除,并将一个新记录添写到`wtmp`文件中。

由UNIX内核提供的基本时间服务是计算协调世界时(UTC)公元1970年1月1日00:00:00这一特定时间以来经历的秒数，这种秒数以数据类型`time_t`表示，称为`日历时间`.

`本地时间`是考虑本地时区和夏令时标志的时间。

UNIX与时间相关的函数如下:

```cpp
#include<time.h>

time_t time(time_t* calptr);    //返回日历时间

struct tm* gmtine(const time_t* calptr);    //将日历时间calptr转换成分解的时间

struct tm* localtime(const time_t* calptr); //将日历时间calptr转换成本地时间

time_t mktime(struct tm* tmptr);    //将本地时间tmptr转换成日历时间
```