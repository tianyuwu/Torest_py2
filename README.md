# torest -- 开箱即用的通用rest api开发框架

## 集成功能
- 基于tornado的异步框架
- docker一键部署环境依赖，实现全平台无缝移植
- 异步数据库操作层，封装了通用的操作，底层支持postgresql，mysql，mongodb三种数据库
- 基于redis的session会话支持
- 基于redis的缓存方案，优雅的缓存读写实现
- 基于mongodb的日志管理系统，优化日志收集体系，良好的标准输出
- 微信api接入
- 七牛云上传


## 依赖
- tornado_redis_session
- log4mongo
- momoko
- motor

## 怎么处理请求和响应？
### 获取数据`handler.get_param()`
get_param封装了wwww-form-data和application/json两种格式提交的参数，不管是常规的get，post请求，还是json格式提交的数据，均可以获取
### 返回数据`handler.write_json()`
返回通用规范的JSON数据

## 如何进行数据操作？
### CRUD实现
### 缓存机制
### 过滤器
### 表单验证

## 如何进行身份认证？
### session/cookie方案
### JWT
#### 如何更新token

## 如何收集，整理，利用日志？
### 日志存储
项目运行中产生的日志都会记录到mongodb数据库中，这样的好处是可以更方便对日志进行查询，分类以及筛选
### 日志收集
`self.log`对象，封装了logging的一些操作，方便在请求过程中实时记录日志
### 日志打印
格式，标准化，内容全面的teriminal输出

## 如何缓存？

## 微信开发相关
