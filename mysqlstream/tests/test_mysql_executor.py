# brief: mysql_executor的测试用例
import json
import unittest
from datetime import datetime, timezone, timedelta
from mysqlstream.tests.test_config import TestConfig
from mysqlstream.mysql_executor import MysqlExecutor
from mysqlstream.mysql_db_pool import MySqlDBPool


class TestMysqlExecutor(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        MySqlDBPool.init_pool(1, 4, **TestConfig.cfg_for_mysql_db_pool())

    def setUp(self) -> None:
        self.table = 'chong.t_user'
        self.now = self._now()

    @staticmethod
    def _now():
        utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt = utc_now.astimezone(timezone(timedelta(hours=8)))
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def test_1(self):
        sql_all = "select * from {}".format(self.table)
        rows = MysqlExecutor.query_multi_rows(sql_all, None)
        for i in rows:
            tid = i['id']
            s = "delete from {table} where id={tid}".format(table=self.table, tid=tid)
            MysqlExecutor.execute(s, None)

        count_sql = "select count(id) as total from {table}".format(table=self.table)
        row = MysqlExecutor.query_one_row(count_sql, None)
        count = row['total']
        self.assertEqual(0, count)

        # insert id1
        id1 = 1
        name1 = 'name1'
        age1 = 10
        raw_urls1 = {}
        urls1 = json.dumps(raw_urls1, ensure_ascii=False)
        a_sql = """insert into {table} (id,name,age,urls,create_ts) value """.format(table=self.table)
        a_sql += """({0},'{1}',{2},'{3}','{4}')""".format(id1, name1, age1, urls1, self.now)
        MysqlExecutor.execute(a_sql, None)

        # select one id1
        select_sql = "select * from {table} where id={id1}".format(table=self.table, id1=id1)
        row = MysqlExecutor.query_one_row(select_sql, None)
        self.assertEqual(row['id'], id1)
        self.assertEqual(row['name'], name1)
        self.assertEqual(row['age'], age1)
        create_ts = row['create_ts'].strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(create_ts, self.now)
        urls = json.loads(row['urls'])
        self.assertEqual(urls, raw_urls1)

        # update id1
        new_name1 = 'new_n"ame1'
        new_age1 = 11
        new_url = {"urls": ["http://@@", "http:\\🤖😁😘'￥%……*）、n"]}
        new_urls1 = json.dumps(new_url, ensure_ascii=False)
        new_create_ts = self._now()
        update_sql = """update {table} set name=%s,age=%s,urls=%s,create_ts=%s""".format(table=self.table)
        MysqlExecutor.execute(update_sql, (new_name1, new_age1, new_urls1, new_create_ts))

        # select one id1
        row = MysqlExecutor.query_one_row(select_sql, None)
        self.assertEqual(row['id'], id1)
        self.assertEqual(row['name'], new_name1)
        self.assertEqual(row['age'], new_age1)
        create_ts = row['create_ts'].strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(create_ts, new_create_ts)
        urls = json.loads(row['urls'])
        self.assertEqual(urls, new_url)

        # insert id2
        id2 = 2
        name2 = 'name2'
        age2 = 20
        raw_url2 = {"urls": ["http:'//@@", "http:\🤖😁'😘￥%……*）、n"]}
        url2 = json.dumps(raw_url2, ensure_ascii=False)
        b_sql = """insert into {table} (id,name,age,urls,create_ts) value """.format(table=self.table)
        b_sql += """(%s,%s,%s,%s,%s)"""
        _, last_id = MysqlExecutor.execute(b_sql, (id2, name2, age2, url2, self.now))
        self.assertEqual(last_id, id2)

        # select one id2
        select_sql = "select * from {table} where id={id2}".format(table=self.table, id2=id2)
        row = MysqlExecutor.query_one_row(select_sql, None)
        self.assertEqual(row['id'], id2)
        self.assertEqual(row['name'], name2)
        self.assertEqual(row['age'], age2)
        create_ts = row['create_ts'].strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(create_ts, self.now)
        urls = json.loads(row['urls'])
        self.assertEqual(urls, raw_url2)

        # select all
        rows = MysqlExecutor.query_multi_rows(sql_all, None)
        self.assertEqual(2, len(rows))
        ids = [id1, id2]
        names = [new_name1, name2]
        ages = [new_age1, age2]
        urls_list = [new_urls1, url2]
        for i in rows:
            tid = i['id']
            index = ids.index(tid)
            ids.pop(index)

            name = i['name']
            index = names.index(name)
            names.pop(index)

            age = i['age']
            index = ages.index(age)
            ages.pop(index)

            url = i['urls']
            index = urls_list.index(url)
            urls_list.pop(index)

        self.assertEqual(ids, [])
        self.assertEqual(names, [])
        self.assertEqual(ages, [])
        self.assertEqual(urls_list, [])

        delete_sql = 'delete from {table} where id=%s'.format(table=self.table)
        MysqlExecutor.execute(delete_sql, [id1])
        rows = MysqlExecutor.query_multi_rows(sql_all, None)
        self.assertEqual(1, len(rows))

        MysqlExecutor.execute(delete_sql, [id2])
        rows = MysqlExecutor.query_multi_rows(sql_all, None)
        self.assertEqual(0, len(rows))

        ids = [10, 11, 12]
        insert_sql = "insert into {table} (id,name,age,urls) value (%s,%s,%s,%s)".format(table=self.table)
        sqls = [insert_sql for i in ids]
        args = [[i, 'name', 1, json.dumps({})] for i in ids]
        MysqlExecutor.transaction_execute(sqls, args)
        rows = MysqlExecutor.query_multi_rows(sql_all, None)
        self.assertEqual(3, len(rows))

        exe = MysqlExecutor()
        exe.start_transaction()
        for i in ids:
            exe.no_commit_execute(delete_sql, [i])
        exe.commit()
        rows = MysqlExecutor.query_multi_rows(sql_all, None)
        self.assertEqual(0, len(rows))

    def test_2(self):
        s = "select * from user where uid=%s"
        args = ['1 and 1=1']
        sql = MysqlExecutor.build_sql(s, args)
        right_sql = "select * from user where uid='1 and 1=1'"
        self.assertEqual(sql, right_sql)


if __name__ == '__main__':
    def suite():
        s = unittest.TestSuite()
        s.addTest(TestMysqlExecutor.test_1)
        s.addTest(TestMysqlExecutor.test_2)
        return s

    runner = unittest.TextTestRunner()
    runner.run(suite())
