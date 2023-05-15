# TerminalsConnectivityTester
大量终端的网络连接性批量测试工具🛠。

Network connectivity test tool for a large number of terminals🛠.

![preview-v0 2 3](https://user-images.githubusercontent.com/31813146/230643284-e1e657aa-beb0-40b4-aad1-e6b110aa3cd4.png)

## 🗝简介 - Brief
当内网中包含大量网络设备，个别不常用的终端连接异常时很难及时被发现，应避免需要使用时才处理异常。

使用此工具可以周期性地对内网中的大量终端进行连通性测试，有助于及时发现网络问题并给予解决。

## 👨🏻‍💻特性 - Features
1. 支持以 .json 格式保存和打开工具测试结果；
2. 支持以 .csv 格式导出和导入工具测试结果；
3. 支持以测试结果筛选列表显示项；
4. 支持以不同颜色区分测试结果；
5. 支持配置 SQL 查询命令直接从 MySQL 数据库转储设备信息以显示并可立即测试；
6. 支持无延迟高速测试模式，及测试间增加延迟的低速模式；
7. 所有设置通过 config.yaml 更改，请保证此配置文件位于软件同目录，不可更名。

## ⚙️使用说明 - Usage
#### 配置文件说明
_**注意缩进且冒号后有一个空格**_

```yaml
# ./config.yaml
# -*- coding: GBK -*-
```
文件名需为“config.yaml”，且与主程序同目录，GBK编码；

```yaml
## MySQL database basic settings
## *hostname(IP), serving port, username, password
database:
  host: localhost
  port: 3306
  username: root
  password: 123456
```
此项定义了数据库基本设置（字典），依次需指定服务主机名(IP)、服务端口、数据库用户名、数据库密码；

```yaml
## All departments and database name lists
departments:
  DeptA: ['a1', 'a2', 'a3']
  DeptB: ['b']
  DeptC: ['c1', 'c2']
```
此项定义了主程序内所有分类名（键）及此分类下所有数据库名列表（值），键值均可修改；

```yaml
## Column IDs and each column's display name and width
## Categorized by the first column by default
## *Modifications may cause early terminals record files to unable to open
columns:
  '#0':       # Necessary, do not change column ID
    fullname: 'Department'
    width: 140
  name:       # Unnecessary, column ID matchs SELECT names below
    fullname: 'Name'
    width: 180
  type:       # Unnecessary, do not change column ID
    fullname: 'Type'
    width: 120
  ip:         # Unnecessary, column ID matchs SELECT names below
    fullname: 'IP Address'
    width: 100
  latency:    # Necessary, do not change column ID
    fullname: 'Latency'
    width: 100
```
此项定义了软件列ID（键），及其显示列名和初始列宽（字典），默认按第一列分类，且至少包含“'#0'”列和“latency”列。软件中“type”列下显示内容将与下一项设置键名对应；

```yaml
## 'type'(terminal's type) and SQL SELECT code for each types
## *Needs 'name'(terminal's name) and 'ip'(terminal's IP)£¬match column IDs
dumpcodes:
  TypeX: "SELECT name, ip FROM tablex"
  TypeY: "SELECT devicename 'name', ip FROM devicetable, iptable WHERE devicetable.deviceid = iptable.deviceid"
```
此项定义了所有设备类型（键）及其SQL查询语句（值），查询结果的列名（或别名）需与上一项设置的列ID对应。

#### 主程序使用说明
菜单项：
```
File                      #   [文件操作]
  ┣ Open ...              # 打开此程序保存的 .json 记录文件
  ┣ Save                  # 
  ┣ Save as ...           # 
  ┣ Import ...            # 
  ┣ Export ...            # 
  ┗ Quit                  # 
Filter                    #   [过滤器]
  ┣ Normal                # 
  ┣ Timeout               # 
  ┣ Unknown               # 
  ┗ Untested              # 
Database                  #   [数据库操作]
  ┣ Dump (Config file)    # 
  ┣ Dump from localhost   # 
  ┗ Dump from remote ...  # 
ConnectivityTest          #   [测试程序]
  ┣ Run (Performance)     # 
  ┗ Run                   # 
About                     #   [关于此程序]
  ┗ TerminalsConnectivityTester
```

主程序基本使用流程：

## 📙更新日志 - Update logs
#### 2023/04/07 - v0.2.3(1)
1. 发布v0.2.3(1)，开发环境基于python 3.11.1。
