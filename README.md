# torest -- 开箱即用的通用rest api开发框架
![](https://img.shields.io/github/license/mashape/apistatus.svg)
## 特色功能
- [x] 基于tornado的异步Web Server
- [x] 基于redis的session会话支持
- [x] 基于redis的缓存方案，优雅的缓存读写实现
- [x] 基于mongodb的日志管理系统，优化日志收集体系，良好的标准输出
- [ ] docker一键部署环境依赖，实现全平台无缝移植
- [ ] 异步数据库操作层，封装了通用的操作，底层支持postgresql，mysql，mongodb三种数据库
- [ ] 微信api接入
- [ ] 七牛云上传
- [ ] 短信，邮件的发送

## 如何运行
### virtualenv方式
1. 部署redis，mongodb，以及postgredb数据库
2. 修改`config.py`中对应的配置项
3. 进入项目根目录，执行下边命令
```
pip install -r requirements.txt
python app.py
```
### docker方式
docker方式运行需要事先安装docker以及docker-compose，在已经安装的前提下，执行运行下边命令
```
docker-compose build
docker-compose up
```


## 怎么处理请求和响应？
### 获取数据
`handler.get_param()`get_param封装了wwww-form-data和application/json两种格式提交的参数，不管是常规的get，post请求，还是json格式提交的数据，均可以获取
### 返回数据
`handler.write_json()`返回通用规范的JSON数据

## 如何进行数据操作？
### CRUD实现
- [ ] 缓存机制
- [ ] 过滤器
- [ ] 表单验证

## 如何进行身份认证？
- [x] session/cookie方案
- [ ] JWT

## 如何收集，整理，利用日志？
### 日志存储
项目运行中产生的日志都会记录到mongodb数据库中，这样的好处是可以更方便对日志进行查询，分类以及筛选
### 日志收集
`self.log`对象，封装了logging的一些操作，方便在请求过程中实时记录日志
### 日志打印
格式，标准化，内容全面的teriminal输出

## 如何缓存？
- [x] 接口缓存
- [ ] 数据库查询缓存

## 微信开发相关
- [ ] 微信授权登录
- [ ] js-sdk签名认证
- [ ] 微信机器人
- [ ] 其他

## 开源协议
MIT License
Copyright (c) 2017 tianyuwu