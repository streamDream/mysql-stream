说明
----

::

    简单的Mysql client和ORM工具类

-  Mysql client包括：

   -  常见的query和execute
   -  特色功能是封装了transaction功能

-  ORM工具类包括：

   -  仅支持针对单个表的CURD操作，暂不支持多表联合的操作
   -  查询操作支持order by，limit等语法
   -  使用方法见test目录下的test\_models.py

-  目前测试过的Python版本为3.6，MySQL服务器版本为5.6

依赖
----

::

        DBUtils==1.3
        PyMySQL==0.10.0

使用说明
--------

一、作为mysql client使用 1. 初始化连接池 2. 使用client相关的方法

.. code:: python

    # brief:
    import json
    from datetime import datetime, timezone, timedelta
    from mysqlstream.mysql_executor import MysqlExecutor
    from mysqlstream.mysql_db_pool import MySqlDBPool


    # 初始化连接池
    MySqlDBPool.init_pool(1, 4, **dict(host='',
                                       port=3306,
                                       username='chong',
                                       password=''))


    class ClientDemo:
        """
        演示MySQL client的使用

            演示的数据表结构如下：
                CREATE TABLE `t_user` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `name` varchar(32) NOT NULL,
                  `age` int(3) NOT NULL,
                  `urls` text,
                  `create_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
        """

        def __init__(self):
            self.table = '{database}.t_user'.format(database='chong')
            self.now = self._now()

        @staticmethod
        def _now():
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
            dt = utc_now.astimezone(timezone(timedelta(hours=8)))
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        def show(self):
            # 增加数据(不带参数的方式执行SQL语句)
            id1 = 1
            name1 = 'name1'
            age1 = 10
            raw_urls1 = {}
            urls1 = json.dumps(raw_urls1, ensure_ascii=False)
            a_sql = """insert into {table} (id,name,age,urls,create_ts) value """.format(table=self.table)
            a_sql += """({0},'{1}',{2},'{3}','{4}')""".format(id1, name1, age1, urls1, self.now)
            affect_rows, last_id = MysqlExecutor.execute(a_sql, None)
            print(affect_rows, last_id)  # 1 1

            # 增加数据(带参数的方式执行SQL语句)
            id2 = 2
            name2 = 'name2'
            age2 = 20
            raw_url2 = {"urls": ["http:'//@@", "http:\🤖😁'😘￥%……*）、n"]}
            url2 = json.dumps(raw_url2, ensure_ascii=False)
            b_sql = """insert into {table} (id,name,age,urls,create_ts) value """.format(table=self.table)
            b_sql += """(%s,%s,%s,%s,%s)"""
            affect_rows, last_id = MysqlExecutor.execute(b_sql, (id2, name2, age2, url2, self.now))
            print(affect_rows, last_id)  # 1 2

            # 查询单行记录
            count_sql = "select count(id) as total from {table}".format(table=self.table)
            row = MysqlExecutor.query_one_row(count_sql, None)
            count = row['total']
            print(count)   # 2

            # 查询多行记录
            sql_all = "select * from {}".format(self.table)
            rows = MysqlExecutor.query_multi_rows(sql_all, None)
            print(rows)
            """
                [
                    {
                        'id': 1, 
                        'name': 'name1', 
                        'age': 10, 
                        'urls': '{}', 
                        'create_ts': datetime.datetime(2020, 9, 23, 16, 23, 35)
                    },
                    {
                        'id': 2, 
                        'name': 'name2', 
                        'age': 20, 
                        'urls': '{"urls": ["http:\'//@@", "http:\\\\🤖😁\'😘￥%……*）、n"]}', 
                        'create_ts': datetime.datetime(2020, 9, 23, 16, 23, 35)
                    }
                 ]
            """

            # 事务化执行多条SQL
            # 方式一：一次给定多条语句和参数的列表
            ids = [10, 11, 12]
            insert_sql = "insert into {table} (id,name,age,urls) value (%s,%s,%s,%s)".format(table=self.table)
            sqls = [insert_sql for i in ids]
            args = [[i, 'name', 1, 'http://www.test.com'] for i in ids]
            MysqlExecutor.transaction_execute(sqls, args)

            # 方式二：多次提交SQL
            ids.append(id1)
            ids.append(id2)
            delete_sql = f'delete from {self.table} where id=%s'
            exe = MysqlExecutor()
            exe.start_transaction()
            for i in ids:
                exe.no_commit_execute(delete_sql, [i])
            exe.commit()

            # 生成转义后的SQL
            s = "select * from user where uid=%s"
            args = ['1 and 1=1']
            sql = MysqlExecutor.build_sql(s, args)
            print(sql)  #  select * from user where uid='1 and 1=1'


    if __name__ == '__main__':
        ClientDemo().show()

二、作为mysql ORM库使用 1. 初始化连接池 2. 创建ORM类 3.
使用ORM相关的方法

.. code:: python

    # brief: 演示ORM的用法
    from datetime import datetime
    from mysqlstream.field_type import StringType, IntegerType, TextType, DatetimeType
    from mysqlstream.models import Model
    from mysqlstream.mysql_db_pool import MySqlDBPool

    # 初始化连接池
    MySqlDBPool.init_pool(1, 4, **dict(host='',
                                       port=3306,
                                       username='chong',
                                       password=''))

    # 创建ORM类
    class User(Model):
        __table__ = '{db}.t_user'.format(db='chong')

        id = IntegerType('id', primary_key=True)
        name = StringType('name', default='')
        age = IntegerType('age')
        urls = TextType()
        create_ts = DatetimeType()


    class OrmDemo:
        """
        演示MySQL ORM的使用

            演示的数据表结构如下：
                CREATE TABLE `t_user` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `name` varchar(32) NOT NULL,
                  `age` int(3) NOT NULL,
                  `urls` text,
                  `create_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
        """

        @classmethod
        def show(cls):
            # 增加一行记录
            id1 = 1
            name1 = 'name1'
            age = 10
            urls1 = {}
            create_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user = User(id=id1, name=name1, age=age, urls=urls1, create_ts=create_ts)
            affected, last_id = user.save()
            print(affected, last_id)  # 1 1

            # 查询记录
            user = User().get(id1)
            print(user)  # id:1,name:name1,age:10,urls:{},create_ts:2020-09-23 16:48:33

            new_name1 = 'new_n"ame1'
            new_age1 = 11
            new_urls1 = {"urls": ["http://@@", "http:\\🤖😁😘'￥%……*）、n"]}
            user.name = new_name1
            user.age = new_age1
            user.urls = new_urls1
            user.create_ts = create_ts
            affected, last_id = user.update()
            print(affected, last_id)  # 1 0
            print(user)
            """
              id:1,name:new_n"ame1,age:11,urls:{'urls': ['http://@@', "http:\\🤖😁😘'￥%……*）、n"]},create_ts:2020-09-23 16:48:33 
            """

            id2 = 2
            name2 = 'name2'
            age2 = 20
            urls2 = {"url": ["http://fdafd.com/'cn.jpg", "http://om.fda.org"]}
            user = User(id=id2, name=name2, age=age2, urls=urls2)
            user.save()

            id3 = 3
            name3 = 'name3'
            age3 = 30
            user = User(id=id3, name=name3, age=age3, urls={"urls": ["http://@@", "http:\🤖😁😘￥%……*）、n"]})
            user.save()

            # 查询数据的总行数
            count = User().count_of_rows('id')
            print(count)  # 3

            # 条件查找多行数据
            users = User().query_all('id>%s', args=[0], order_by='id desc', limit=(0, 10))
            print(users)

            """
                [  id:3,name:name3,age:30,urls:{'urls': ['http://@@', 'http:\\🤖😁😘￥%……*）、n']},create_ts:0000-00-00 00:00:00, 
                   id:2,name:name2,age:20,urls:{'url': ["http://fdafd.com/'cn.jpg", 'http://om.fda.org']},create_ts:0000-00-00 00:00:00, 
                   id:1,name:new_n"ame1,age:11,urls:{'urls': ['http://@@', "http:\\🤖😁😘'￥%……*）、n"]},create_ts:2020-09-23 16:48:33
                ]
            """

            # 根据ID删除数据
            u1 = User(id=id1)
            u1.delete()

            u2 = User(id=id2)
            u2.delete()

            u3 = User(id=id3)
            u3.delete()


    if __name__ == '__main__':
        OrmDemo.show()
