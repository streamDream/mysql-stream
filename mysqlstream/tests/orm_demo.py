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
