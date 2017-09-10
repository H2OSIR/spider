# A simple framework of spider

if you want to writer a http-crawler program, this framework can help you do it better.Here are some simple introductions.
 
## spider.http_requests

In this script, you can wrap your own class like requests if you want.

* spider.http_requests.random\_userAgent
	
	if your frequecy of the request is too fast, you can use it Instead of your original user-Agent in your headers , like this:
    	
	``` python
	# -*- coding:utf-8 -*-
	# python3

	from http_requests import random_userAgent
	
	headers = {'user-Agent': random_userAgent}
	```

* spider.http_requests.HTTP\_Status\_Code

	if you want to know the Chinese meaning of the request status, you can check or use this dict.
		
	```python
	# -*- coding:utf-8 -*-
	# python3

	import requests
	from http_requests import HTTP_Status_Code

	response = requests.get('https://www.baidu.com')
	status = response.status
	print(status)
	print(HTTP_Status_Code[status])

	>>> 200
	>>>（成功） 服务器已成功处理了请求。 通常，这表示服务器提供了请求的网页。 
	```


## spider.parse_html

In this script, you can according to your specific needs to write python function or class. sorry for there is no example.


    
		
