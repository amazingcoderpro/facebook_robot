# 启动说明
## 1.web server
```
cd webservice
pipenv shell
python3 manager.py runserver
```

## 2.任务调度系统
```
pipenv shell
python3 main.py [pro|test]  [restart|new]
```
*例: python3 main.py test restart* 

*注：*

[pro|test] 指定环境信息 
- pro 代表生产环境, 服务器地址 47.112.113.252, 对应配置文件为config/config.yaml
- tes 代表测试环境, 推荐开发人员自测时使用, 服务器地址：10.252.252.67, 对应配置文件为config/config_test.yaml  

[restart|new] 指定任务启动模式
- restart 代表将对数据库中所有未结束的任务重新启动, 但并不会清除已经存在的job, 多用于系统宕机后重启或本地测试
- new 代表仅启动状态为‘new’的任务 

## 3.Worker
```
pipenv shell
celery -A tasks.workers -Q default,China,North_American,Japan worker -l info -c 4 -Ofair -f logs/celery.log -env test
```
*备注：*
- -Q 指定了接收任务的队列
- -l 指定日志级别
- -c 指定并发数
- -Ofair 禁用预取
- -f 指定celery日志存放目录, 若不指定日志将输入在控制台
- -env 参数指定了环境信息，可选项为pro或test, 请保持与任务调度系统启动时的环境信息一致。

## 其他
建议开发人员使用test环境, 即在2,3指定test参数, 可以通过修改config_test.yaml来调整系统运行时的一些参数