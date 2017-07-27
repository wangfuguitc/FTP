introduction			FTP
author:				文奇
time：				2017/7/27
need environment		python3.5


功能介绍：
实现简单文件传输,支持登录认证,多用户同时登录,md5校验,断点续传,限制磁盘空间大小


用法:
服务端启动bin目录下的start_server.py,客户端启动bin下staert_client.py后输入服务端的ip地址及端口开始连接
登录用户（wangfugui/123和richwang/123），在conf目录下的user__data（用户名、密码、磁盘空间）
上传和下载（get和put）
查看目录，切换目录，创建文件夹，删除文件或文件夹（dir、cd、mkdir、remove）
开启或关闭md5验证（MD5 on或MD5 off）
