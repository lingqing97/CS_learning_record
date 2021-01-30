### chapter8 IO库

#### 8.1 IO类

* `iostream`定义了用于读写流的基本类型，`fstrem`定义了读写命名文件的类型，`sstream`定义了读写内存`string`对象的类型
  * <font color=red>我们不能拷贝或对IO对象赋值</font>
  * 由于不能拷贝IO对象，因此我们也不能将形参或返回类型设置为流类型，进行IO操作的函数通常以引用方式传递和返回流
  * 读写一个IO对象会改变其状态，因此传递和返回的引用不能是`const`的
* IO类定义了一些函数和状态标志，可以帮助我们访问和操作流的条件状态（见例子一）
  * 使用`good()`或`fail()`来确定流的总体状态，使用`bad()`判断是不全面的
* 每个输出流都管理一个缓冲区，用来保存程序读写的数据，执行输出运算后，可能会立刻输出结果，也有可能被操作系统保存在缓冲区中，随后再打印
  * 我们可以使用操纵符如`endl`来显示刷新缓冲区

```cpp
//例子一：IO库条件状态
strm::badbit            //表示系统级错误，如不可恢复的读写错误，发生此错误则流就无法再使用了
strm::failbit           //表示发生可恢复错误，这种错误可以修正，流还可以继续使用
strm::eofbit            //指出流到达了文件结束
strm::goodbit           //指出流未处于错误状态

s.eof()                 //若流s的eofbit置位，则返回true
s.fail()                //若流s的failbit或badbit置位，则返回true
s.bad()                 //若流s的badbit置位，则返回true
s.good()                //若流s处于有效状态，则返回true

s.clear()               //将流s所有条件状态位复位，将流的状态设置为有效，返回void

```

#### 8.2 文件输入输出

* 头文件`fstream`定义了三个类型类支持文件`IO:ifstream`从一个给定文件读取数据,`ofstream`向一个给定文件写入数据，以及`fstream`可以读写给定文件
* 当一个`fstream`对象被销毁时，`close`会自动调用
* 每个流都有一个关联的`文件模式`,用来指出如何使用文件（见例子三）
  * 保留被`ofstream`打开的文件中已有数据的唯一方法是显式指定`app`或`in`模式
  * 使用`open`函数时，文件隐式地以`out`(写)模式打开

```cpp
//例子一：fstream特有的操作
fstream fstrm;          //创建一个未绑定的文件流，fstream是头文件fstream中定义的一个类型
fstream fstrm(s);       //创建一个fstream，并打开名为s的文件，s可以是string类型或者一个指向c风格字符串的指针
fstream fstrm(s,mode);  //按指定mode打开文件
fstrm.open(s);          //打开名为s的文件，并将文件与fstrm绑定
fstrm.close();          //关闭与fstrm绑定的文件
fstrm.is_open();        //返回一个bool值，指出与fstrm关联的文件是否成功打开且尚未关闭

//例子二：打开文件的正确方式
ifstream ifs(filename);
if(ifs){    //判断是否正确打开
    //...
}
else{
    cerr<<//...
}

//例子三：文件模式
in                      //以读方式打开
out                     //以写方式打开
app                     //每次写操作前定位到文件末尾
ate                     //打开文件后立刻定位到文件末尾
trunc                   //截断文件
binary                  //以二进制方式进行IO

ofstream out("file1");          //隐含以输出模式打开文件并截断文件
ofstream out2("file1",ofstream::out);
//为了保留文件内容，我们必须显式指定app模式
ofstream app("file1",ofstream::app);
```

#### 8.3 string流

* `istringstream`从`string`读取数据，`ostringstream`向`string`写入数据，而头文件`stringstream`既可从`string`读数据也可向`string`写数据

```cpp
//例子一：stringstream特有的操作
sstream strm;               //strm是一个未绑定的stringstream对象
sstream strm(s);            //strm是一个sstream对象，保存string s的一个拷贝
strm.str();                 //返回strm所保存的string的拷贝
strm.str(s);                //将string s拷贝到strm中。返回void

//例子二:使用string流的例子

struct PersonInfo{
    string name;
    vector<string> phones;
};

string line,word;                   //分别保存来自输入的一行和单词
vector<PersonInfo> people;          //保存来自输入的所有记录
//逐行从输入读取数据，直至cin遇到文件尾（或其他错误）
while(getline(cin,line)){
    PersonInfo info;                //创建一个保存此记录数据的对象
    istringstream record(line);     //将记录绑定到刚读入的行
    record>>info.name;              //读取名字
    while(record>>word)             //读取电话号码
        info.phones.push_back(word);//保持它们
    people.push_back(info);         //将此记录追加到people末尾
}

```
