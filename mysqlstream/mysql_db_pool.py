# brief: DB的链接池
import pymysql
from DBUtils.PooledDB import PooledDB


class MySqlDBPool:
    _pool = None  # 连接池对象

    @classmethod
    def init_pool(cls, min_idle_connections, max_connections,
                  host, port, username, password, charset='utf8mb4',
                  cursor_class=pymysql.cursors.DictCursor):
        """
        初始化连接池，app全局调用一次就够了！
        :param min_idle_connections   最小的空闲链接数
        :param max_connections  最大的链接数
        :param host  MySQL的地址
        :param port  MySQL的端口号
        :param username  MySQL的用户名
        :param password  MySQL的密码
        :param charset  MySQL的字符集
        :param cursor_class  使用的cursor类型
        """
        cls._pool = PooledDB(pymysql,
                             min_idle_connections,
                             maxconnections=max_connections,
                             host=host,
                             user=username,
                             passwd=password,
                             port=port,
                             charset=charset,
                             cursorclass=cursor_class)

    def __init__(self):
        self._connection = None

    def get_connection(self):
        """
        获取连接
        """
        if not self._pool:
            raise Exception("The class method init() must be invoke at first!")

        self._connection = self._pool.connection()
        return self._connection

    def recycle_connection(self):
        """
        回收连接
        """
        self._pool.cache(self._connection)

    def __enter__(self):
        connections = self._pool._connections
        # print('>>>> MysqlDBPool enter, connections:', connections)
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        connections = self._pool._connections
        # print('>>>> MysqlDBPool exit, connections:', connections)
        self.recycle_connection()
