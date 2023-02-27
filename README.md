# schedule_bot
------

一个基于go-cqhttp开发的郑州大学课程提醒机器人，能在上课前将要上的课程相关信息发送给指定qq用户/群



### 效果图

------

<img style="height:500px" src="http://150.158.139.2/markdown/sc_bot/2.png">



### 部署

------

- 在[Releases · Mrs4s/go-cqhttp (github.com)](https://github.com/Mrs4s/go-cqhttp/releases)下载并配置go-cqhttp, 首次运行选择正向websocket并进行相关配置
- 首次运行登陆教务系统打开课程表页面，把整个页面的html复制到all.txt![](http://150.158.139.2/markdown/sc_bot/1.png)
- 在config.yaml中进行相关配置
- 安装requirements.txt中包
- 运行main.py
