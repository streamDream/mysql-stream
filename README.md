## 说明
#### 简单的Mysql client和ORM工具类
   + Mysql client包括：
     * 常见的query和execute
     * 特色功能是封装了transaction功能
   
   + ORM工具类包括：
     * 仅支持针对单个表的CURD操作，暂不支持多表联合的操作
     * 查询操作支持order by，limit等语法
     * 使用方法见test目录下的test_models.py
     
* 目前测试过的Python版本为3.6，MySQL服务器版本为5.6


## 依赖
```
    DBUtils==1.3
    PyMySQL==0.10.0
```

