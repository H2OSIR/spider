# 号码搜索文档

> 因包含敏感信息，脚本中的相关字段会用 * 号代替。

通过 https://www.baidu.com 和 https://www.so.com 查询电话号码，获取该号码的归属地和标记信息。

## 基本思路

- [args.py]()　　　	　　　**从数据库获取号码列表** 

- [args.py]()　　　	　　　**从互联网上获取可用的代理IP**

- [http_requests.py]()　　**组合好参数后，去目标网站进行搜索，返回 html 的列表**

- [parse_html.py]()　　　	**多进程或多线程解析html，返回字典列表**

- [database.py]()　　　　**将字典列表数据，批量插入数据库**

- [run.py]()  　　　　　　　**为方便定时任务封装的主程序**

- [timming_tasks.py]()　　**由于每次可查的号码数有限，因此需要写成周期性定时任务**

- [log/**.log]()　　　　　　**日志**


## 代码中的注意事项

1. 因为定时任务的关系，在做数据操作的时候，本来想用 `sqlalchemy` 库来操作数据库，后来发现会报Python程序异常，具体原因未知。之后就改用 `cx_Oracle` 库，解决了这个问题。可能和自己使用了 `pandas.DataFrame.read_sql` 和 `pandas.DataFrame.to_sql` 有关，后来验证发现，该函数适合一次读取大量数据，对于小量数据，其速度还没有 `cx_Oracle` 的操作快。

2. 线程问题，由于每个号码都要进行百度与好搜两个网站的搜索，因此作者将百度与好搜写成了两个线程的形式。当搜索1个号码时，百度与好搜同时进行搜索，二者互不影响。因此对于多个号码的查询，在网络请求部分，作者在外层使用的是多进程，每个进程包含百度、好搜两个线程，在html解析的部分，也是使用的多进程，因为解析属于CPU密集型，有文章说道CPU密集型的处理，多进程比多线程更快。

3. 应多次调试，找到最佳的查询数、 进程数的组合。该爬虫每次查询50个号码，网络请求是2个进程+2个线程，html解析是4个进程，比较稳定，不容易发生请求异常。

## 脚本文档

### timming_tasks.py 

> 定时任务，运行该脚本，程序会根据配置，周期性的执行主程序 `run.py` 中的 `start(**kwargs)`。

- **timming_tasks.Schedual**

	封装的自定义类

- **timming_tasks.Schedual.generate_sql()**

	一个方法，根据最近的一个日志文件中的最后一个sql语句，判断出最近查询到数据库中的哪一条数据，然后生成一个新的sql语句。这么做是为了避免查询重复的数据。

- **timming_tasks.Schedual.start_task()**
	
	定时任务的主函数，可配置周期，只需修改 `s.enter(5, 0, self.start_task, ())` 中的第一个参数即可，当前为5s。该周期是指里面的主程序结束后，隔多少秒再次运行该程序。

- **timming_tasks.Schedual.run()**

	定时任务的启动函数，运行该函数即开启定时任务，首次执行不需要等待时间，因此，该函数中的 `s.enter(0, 0, self.start_task, ())` 第一个参数为0。

- **run.LOG_NAME**

	生成日志文件名，日期.log。

### run.py

> 爬虫功能主程序，从生成参数，到插入数据库。

- **run.start()**

	主程序

- **run.sql()**

	生成sql语句

### args.py

> 参数组合脚本，为方便网络请求以及携带相关字段信息，组合参数。

- **args.extract_args()**

	根据sql从数据库读取查询参数

- **args.extract_IP()**

	从网络获取代理IP，组合成`requests`库的`proxies`参数形式返回。

- **args.extract()**

	将上面两个函数的结果组合成最终的查询参数，提供给`http_requests.py`.

### http_requests.py

> 网络请求部分，在该脚本中完成。

- **全局变量**

	- User_Agent_list : user_agent列表
	- random_userAgent : 随机从User_Agent_list中取一个user_agent。
	- FIRST_URL : dict, 搜索引擎所对应的网址。
	- HEADERS : 用于 `requests` 的 `headers`


- **http_requests.get_cookies()**

	获取搜索引擎的cookies

- **http_requests.get_html()**

	获取搜索结果的 html

- **http_requests.MyThread()**

	自定义封装的带返回值的多线程类，方便两个引擎同时开启。

- **http_requests.search()**

	将两个引擎用两个线程启动，每一个号码都同时搜索两个引擎，返回一个列表，包含两个元素，分别是各引擎搜索结果的 html。单个号码的查询，可调用该方法

- **http_requests.multi_search()**

	多进程查询多个号码（参数列表），可设置单进程。

### parse_html.py

> 解析搜索结果的 html

- **parse_html.Phone()**

	声明所需的字段属性，作为父类，将被下面两个子类继承。

- **parse_html.BaiduHtml(Phone)**

	一个类，解析百度的搜索结果，内部的方法用于解析不同的字段。

- **parse_html.HaosouHtml(Phone)**

	一个类，解析好搜的搜索结果，内部的方法用于解析不同的字段。

- **parse_html.parse()**

	解析 html，返回一个 dict， key为所需字段属性， value为对应的值。其参数需求请查看脚本代码。

- **parse_html.multi_parse()**

	同 `http_requests.multi_search()`，多进程解析 html。也可以使用多线程，只需要将脚本前面的 `from multiprocessing import Pool` 改成 `from multiprocessing.dummy import Pool` 即可。

### database.py

> 数据库操作，包括读取(读取参数)、写入(数据存储)。

- **全局变量**

	- 数据库的基本参数
	- OUTPUT_TABLE 输出的表名，不是必要的，可在脚本具体代码中写死。
	

- **database.Connect()**

	一个类，创建数据库连接，并包含一些读取数据库和插入数据库的方法。

- **database.Connect().read_sql()**

	参数为一段sql代码，字符串类型，从数据库读取数据，返回 `pandas.DataFrame` 类型的数据。

- **database.Connect().write_sql(data, table)**

	写入数据库，data 参数为字典列表， table 参数为输出表名。

	> <font color=red >注意：
	> 在读取数据库的时候使用的是 `pandas.DataFrame.read_sql()`方法，但是在写入数据库的时候，不管连接用的是 `sqlalchemy` 库，还是 `cx_Oracle` ，如使用 `pandas.DataFrame.to_sql()` 多次对数据库进行操作都会使得python程序发生异常。因此在写入数据库的时候，需要用到 `cx_Oracle` 中的原始方法，批量插入，具体的操作方式可查看脚本代码，或搜索其他网络博客知识。</font>

- **database.Connect().get_maxID()**

	获取输出表中，最大的ID号， 用于为新的数据插入一批不同于数据库的ID。

- **database.Connect().add_index()**

	为输出结果数据批量添加ID，同时该ID必须与数据库中已有的不一致，脚本中实现的是连续增加。


### log/..

> 日志目录

- **record_sql.log**

	记录每一次查询的sql，每次任务开启时，会读取该文件最后一行，以获取上一次的查询记录。

- **\*\*\*\*.log**

	记录程序的异常信息。