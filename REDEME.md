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

## 为什么不使用ORM