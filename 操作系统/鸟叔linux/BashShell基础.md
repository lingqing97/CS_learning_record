### Linux的层次结构

![](../../image/26bfc37e0816586b3a8e545e1636d8c8.png)

### Bash shell基础

##### 常用快捷键

![](../../image/4f4ffd3c974721389aa5d5b71854d6fb.png)

##### 给指令取别名:alias

```shell
#alias:命名别名设置功能  

alias lm='ls -al'  

#取消设置的命令别名:unalias  

unalias lm
```

##### 查看历史命令记录:history

![](../../image/d5823ac3195ba737fd4750b08ca04090.png)

##### 查询指令类型:type

`type [-ta] name`
```shell
选项与参数:
不加任何选项与参数时，type会显示出name是外部指令还是bash内置指令  
-a:会由PATH变量定义的路径中，将所有含有name的指令都列出来，包含alias定义的别名  
-t:当加入-t时，type会以以下字眼显示出他的意义：  
    * file:表示为外部指令
    * alias:表示该命令为别名设置的名称
    * builtin:表示该指令为bash内置的指令功能
```


> ![](../../image/abaebeb1322cd4fc201dabaff76b1a0a.png)  
> ![](../../image/9ed363aab12425f26829cacc94d648a3.png)  
> ![](../../image/318c0dabd60df16ccf418cf8f4c807a0.png)

##### Shell的变量

###### 打印变量:echo

> echo $变量名(不用加括号)  
> ![](../../image/4d5371f84617bbb2b6baf233ecd8c9fe.png)

###### 创建变量的规则

1.变量的赋值使用等号"="，且等号两边不能直接接空白符号

```
myname=bird (true)
myname= bird(false,等号右边右空格)
myname=bird tsai(false,等号右侧有空格)

```

![](../../image/39fe9403e92fa24290137da550da0a1c.png)  
2.变量名只能是英文字母,数字,下划线，且开头字符不能是数字

```
2myname=bird(false)
my_name=bird(true)

```

![](../../image/e694b712f2063ff98b90ad8aab40165b.png)  
3.使用''或者""来定义字符串,**双引号内的特殊字符比如$等可以保有原来的特性，单引号内的特殊字符则全部视为一般字符(纯文本0**

```
var='hello wordl!'(true)
var="hello word!"(false,感叹号'!'是bash shell中特殊字符)
var="lang is $LANG"<==等价于var="lang is zh_TW.UTF-8"
var='lang is $LANG' <==等价于var='lang is $LANG'

```

![](../../image/302a563d7de11ac6999058aa34536fd6.png)  
![](../../image/f7a88d54028b3895a9ef38c217fb67e9.png)  
4.使用""将特殊字符变成一般字符  
![](../../image/d56311809a50a5fee3d5214ffcfb9e7f.png)  
5.将指令的结果赋值给变量，使用`$(指令)`

```
#将本机版本赋值
version=$(uname -r)
version="the version is $(uname -r)"（注意一定要用双引号,这样才可以保留$的功能）

```

![](../../image/b34c6829f5d8898a156e5ca28643f1e3.png)  
![](../../image/f567070f98edb6f8414e0a90d4ebf898.png)  
6.改变环境变量，并将该环境变量应用于整个系统,使用export

```
cd ~
vim .bashrc<==.bashrc文件在Linux刚启动时会执行
export PATH="$PATH:/home/bin"<==将PATH修改，并应用于整个系统
source .bashrc

```

![](../../image/fabf1b2bf384be30fe72d6653851521b.png)  
![](../../image/aeb59638aaf732a9b015b3444af90f05.png)  
重启系统后，发现PATH改变  
![](../../image/edc1ed56a716a1cd2e73aacb229b80e7.png)  
7.通常大写字符为系统默认变量，自行设置变量可以使用小写字符，方便判断  
8.取消变量的方法为使用unset

```
unset myname<==取消myname这个变量

```


> **Hit:子程序仅会继承父程序的环境变量，子程序不会继承父程序的自订变量**

###### 变量键盘读取

`read [-pt] variable`
```
选项与参数:  
-p: 后面可以接提示字符!  
-t: 后面可以接等待的“秒数”  
```

> ![](../../image/606557f6c4ff2ccb4286e9bfb95273fd.png)  

> ![](../../image/7ab82f54935f27c6dc700e7813815987.png)

###### 变量内容的删除、取代与替换（*）

![](../../image/aecdf41017fd545b6c4fc52448247029.png)

###### 万用字符与特殊符号

![](../../image/d243c3a3d0566d5711790f18684bb1f1.png)  
![](../../image/e964b0d28985e0e3fbf900df17007f07.png)

##### 数据流重导向

数据流重导向就是将某个指令执行后应该要出现在屏幕上的数据，给他传输到其他地方，例如文件或者设备(例如打印机之类的)  
![](../../image/7d802b5ad5c3a8441363bc0ed4aba51c.png)  
![](../../image/23a75060c2279b2f647b7e3d651b28e6.png)  
![](../../image/2b21b131349766f37b7d51ae2ba9797b.png)

##### 命令的执行顺序

| 指令下达情况 | 说明  |
| --- | --- |
| cmd1;cmd2 | 顺序执行，无论cmd1是否正确执行，都会执行cmd2 |
| cmd1 && cmd2 | 若cmd1执行完毕且正确执行，则开始执行cmd2;若cmd1执行完毕且为错误,则cmd2不执行 |
| cmd1 \| cmd2 | 若cmd1执行完毕且正确执行，则cmd2不执行；若cmd1执行完毕且错误，则开始执行cmd2 |

**识记要点:指令的执行逻辑与程序设计中的执行逻辑类比**

```
#先判断 /tmp/abc目录是否存在,若不存在则创建/tmp/abc这个目录，之后在该目录下创建hehe文件
ls /tmp/abc || mkdir /tmp/abc && touch /tmp/abc/hehe <==等价于(cmd1 || cmd2) && cmd3

#若/tmp/bvirding文件存在就打印"exist",否则就打印"not exist"
ls /tmp/bvirding && echo "exist" || echo "not exist"

```

##### 管道命令

管道命令仅能处理经由前面一个指令传来的正确信息，也就是standard output的信息，对于stdandard error并没有直接处理的能力  
![](../../image/c3acb9552acd65119cd16bff561e31e2.png)

> 简单讲，就是第一个命令正确的处理结果作为第二个命令的输入，以此类推。

###### 截取命令:cut,grep

> cut -d '分割字符' -f 要取的段  
> 选项与参数:  
> -d: 后面接分割字符，与 -f一起使用  
> -f：依据-d的分割字符将一段讯息分区成为数段，用-f取出第几段的意思  
> ![](../../image/2e99fc4ef0b282200b62d25003eb8703.png)  
> ![](../../image/6346ba3ac495a1584b5f23d992e624c4.png)  
> grep \[-v\] '搜寻字符' \[file or stdin\]  
> 选项与参数:  
> -v:加上-v表示搜寻不包含搜寻字符的行，不加-v则搜寻包含搜寻字符的行  
> ![](../../image/c1f494f1a8656b172d8bc38f23cbae2d.png)

###### 排序命令:sort

> sort \[-futkn\] \[file or stdin\]  
> 选项与参数:  
> -f :忽略大小写的差异，比如A与a视为相同  
> -u:就是uniq,将相同的数据合并，仅显示一行代表  
> -t:与-k配合使用，后面接分割符号，默认按\[tab\]来分割  
> -k:以那个区间来进行排序  
> -n:使用“纯数字”进行排序（默认是以文字体态来进行排序的）  
> ![](../../image/80158b8db477b87625b7b6490d59bb33.png)

###### 双向重导向:tee

> tee \[-a\] file  
> 选项与参数:  
> -a:以累加的方式，将数据加入file当中  
> ![](../../image/36db0d55dd317f89ac01e654e39255b8.png)

###### 字符转换命令:tr

tr可以用来删除一段讯息当中的文字，或者是进行文字讯息的替换!

> 删除讯息的用法:  
> tr \[-d\] SET1  
> 选项与参数:  
> -d:删除讯息当中的SET1这个字串  
> 替换讯息的用法:  
> tr SET1 SET2  
> 选项与参数：  
> 将所有的SET1替换为SET2  
> ![](../../image/308538232c93fe1755e490e05acba720.png)

###### 分区命令:split

> split \[-bl\] file \[PREFIX\]  
> 选项与参数:  
> -b:后面可以接欲分区成的文件大小，可加单位，例如b,k,m等  
> -l:以行数来进行分区  
> PREFIX:可以作为分区文件的前导文字  
> ![](../../image/ec610e5fd0fe3e821c62f53ad42db788.png)

###### 关于减号-的用途

![bb9e8a3cd1a2a4ac51ec6a31abd234ba.png](../../image/d1bb8c14633c41629af77fe59bbfcf61.png)