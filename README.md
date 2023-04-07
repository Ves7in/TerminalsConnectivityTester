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

## 📙更新日志 - Update logs
#### 2023/04/07 - v0.2.3(1)
1. 发布v0.2.3(1)，开发环境基于python 3.11.1。
