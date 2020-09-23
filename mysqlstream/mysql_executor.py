# brief: 基于连接池的mysql执行器
from .mysql_db_pool import MySqlDBPool


class MysqlExecutor:
    def __init__(self):
        self._db_pool = MySqlDBPool()
        self._connection = self._db_pool.get_connection()

    @classmethod
    def _execute_query(cls, sql, args, fetchone=False):
        with MySqlDBPool() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, args)
                if fetchone:
                    rows = cursor.fetchone()
                else:
                    rows = cursor.fetchall()
                return rows

    @classmethod
    def query_one_row(cls, sql, args):
        """
        查询单行结果
        :param  sql: sql的集合，规则和execute()相同
        :param args: args的集合，规则和execute()相同
        :return: 符合的数据结果
        :rtype: None or dict
        """
        return cls._execute_query(sql, args, True)

    @classmethod
    def query_multi_rows(cls, sql, args):
        """
        查询多行结果
        :param  sql: sql的集合，规则和execute()相同
        :param args: args的集合，规则和execute()相同
        :return: 符合的数据结果集合
        :rtype: list of dict
        """
        return cls._execute_query(sql, args)

    @classmethod
    def execute(cls, sql, args):
        """
        执行指定的sql
        :param sql: 需要执行的sql语句
        :param args: 和sql中占位符对应的参数集合
        :type args: tuple, list or dict

        :return: 受影响的行数和本次insert操作的数据的ID(如果在sql中指定了ID，则和指定的ID相同)
        :rtype: int, int

        如果args是list或tuple, 则使用%s作为占位符
        如果args是dict, 则使用%(name)s作为占位符(name是dict的key)

        例如：
            eg1:
                sql = "insert into user (name,age,sex) value(%s,%s,%s)"
                args = ["ChongChong", 3, 1]

            eg2:
                sql = "insert into user (name,age,sex) value (%(n)s,%(a)s,%(s)s)"
                args = {"n": "ChongChong", "a": 3, "s": 1}
        """
        if not sql:
            raise ValueError('sql is empty!')

        with MySqlDBPool() as connection:
            with connection.cursor() as cursor:
                affected = cursor.execute(sql, args)
                connection.commit()
                return affected, cursor.lastrowid

    @classmethod
    def transaction_execute(cls, sql_list, args_list, rollback=True):
        """
        在一个事务中运行多条sql语句,默认失败后自动回滚
        :param  sql_list: sql的集合，规则和execute()相同
        :param args_list: args的集合，规则和execute()相同（可为None，此时sql_list必须自行格式化好的SQL语句）
        """
        if not sql_list:
            raise ValueError('sql_list is empty!')

        try:
            with MySqlDBPool() as connection:
                connection.begin()
                with connection.cursor() as cursor:
                    for i, sql in enumerate(sql_list):
                        if args_list:
                            cursor.execute(sql, args_list[i])
                        else:
                            cursor.execute(sql)
                connection.commit()
        except Exception as e:
            if rollback:
                connection.rollback()
            raise e

    @classmethod
    def build_sql(cls, sql, args):
        """
        构造防SQL注入的语句. 针对args中的特殊字符,做和转义.
        :param sql: 需要执行的sql语句
        :param args: 和sql中占位符对应的参数集合

        :rtype str:
        """
        with MySqlDBPool() as connection:
            with connection.cursor() as cursor:
                return cursor.mogrify(sql, args)

    def start_transaction(self):
        """
        开始事务
        """
        self._connection.begin()

    def no_commit_execute(self, sql, args):
        """
        不自动提交地执行sql（事务处理时使用）
        :param  sql: sql的集合，规则和execute()相同
        :param args: args的集合，规则和execute()相同
        """
        if not sql:
            raise ValueError('sql is None!')
        self._connection.cursor().execute(sql, args)

    def commit(self):
        """
        提交
        """
        self._connection.commit()

    def rollback(self):
        """
        回滚
        """
        self._connection.rollback()
