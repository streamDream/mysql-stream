# brief: 演示client的用法
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
        self.table = 'chong.t_user'
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
