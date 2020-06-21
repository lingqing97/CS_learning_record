### 使用MySQL

- 连接:为了连接到MySQL，需要以下信息:
  - 主机名:若连接到本地则为localhost
  - 端口:如果使用默认**端口3306**之外的端口
  - 一个合法的用户名
  - 用户口令（如果需要）
- 连接数据库:使用`USE`关键字选择数据库
```sql
USE course; /*输出Database changed*/
```
- 了解数据库和表:
  - `show databases;`指令返回可用数据库的一个列表.
  - `show tables`指令获得一个数据库内的表的列表.
  - `show columns from 表名`指令要求给出一个表名，它对每个字段返回一行，每行包含该字段的详细信息。
  - `help show`指令显示允许的SHOW语句。
