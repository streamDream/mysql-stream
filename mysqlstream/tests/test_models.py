# brief: models的单元测试
import unittest
from datetime import datetime
from mysqlstream.tests.test_config import TestConfig
from mysqlstream.field_type import StringType, IntegerType, TextType, DatetimeType
from mysqlstream.models import Model
from mysqlstream.mysql_db_pool import MySqlDBPool


class User(Model):
    __table__ = 'chong.t_user'

    id = IntegerType('id', primary_key=True)
    name = StringType('name', default='')
    age = IntegerType('age')
    urls = TextType()
    create_ts = DatetimeType()


class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        MySqlDBPool.init_pool(1, 4, **TestConfig.cfg_for_mysql_db_pool())

    def test_1(self):
        user = User()
        users = user.query_all()
        for u in users:
            uid = u.id
            User(id=uid).delete()

        users = user.query_all()
        self.assertEqual(0, len(users))

        id1 = 1
        name1 = 'name1'
        age = 10
        urls1 = {}
        create_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = User(id=id1, name=name1, age=age, urls=urls1, create_ts=create_ts)
        count, last_id = user.save()
        self.assertEqual(1, count)
        self.assertEqual(id1, last_id)

        user = User().get(id1)
        self.assertEqual(id1, user.id)
        self.assertEqual(name1, user.name)
        self.assertEqual(urls1, user.urls)
        self.assertEqual(create_ts, user.create_ts)

        new_name1 = 'new_n"ame1'
        new_age1 = 11
        new_urls1 = {"urls": ["http://@@", "http:\\🤖😁😘'￥%……*）、n"]}
        user = User()
        user.id = id1
        user.name = new_name1
        user.age = new_age1
        user.urls = new_urls1
        user.create_ts = create_ts
        count, last_id = user.update()
        self.assertEqual(1, count)

        user = User().get(id1)
        self.assertEqual(user.id, id1)
        self.assertEqual(user.name, new_name1)
        self.assertEqual(user.age, new_age1)
        self.assertEqual(user.urls, new_urls1)
        self.assertEqual(user.create_ts, create_ts)

        id2 = 2
        name2 = 'name2'
        age2 = 20
        urls2 = {"url": ["http://fdafd.com/'cn.jpg", "http://om.fda.org"]}
        user = User(id=id2, name=name2, age=age2, urls=urls2)
        user.save()

        user = User().get(id2)
        self.assertEqual(user.id, id2)
        self.assertEqual(user.name, name2)
        self.assertEqual(user.age, age2)
        self.assertEqual(user.urls, urls2)

        count = User().count_of_rows('id')
        self.assertEqual(2, count)

        id3 = 3
        name3 = 'name3'
        age3 = 30
        user = User(id=id3, name=name3, age=age3, urls={"urls":["http://@@","http:\🤖😁😘￥%……*）、n"]})
        user.save()

        ids = [id1, id2, id3]
        names = [new_name1, name2, name3]
        users = User().query_all(where='id>0')
        for u in users:
            index = ids.index(u.id)
            ids.pop(index)

            index = names.index(u.name)
            names.pop(index)
            u.delete()

        self.assertEqual(ids, [])
        self.assertEqual(names, [])

        count = User().count_of_rows('id')
        self.assertEqual(0, count)


if __name__ == '__main__':
    unittest.main()
