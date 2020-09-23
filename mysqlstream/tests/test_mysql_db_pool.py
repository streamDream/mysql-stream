# brief: mysql_db_pool的测试用例
import unittest
from mysqlstream.tests.test_config import TestConfig
from mysqlstream.mysql_db_pool import MySqlDBPool


class TestMysqlDBPool(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        MySqlDBPool.init_pool(1, 4, **TestConfig.cfg_for_mysql_db_pool())

    def setUp(self) -> None:
        self.mysql_db_pool = MySqlDBPool()

    def test_1(self):
        """
        方法功能测试
        """
        self.assertEqual(MySqlDBPool._pool._connections, 0)
        self.mysql_db_pool.get_connection()
        self.assertEqual(MySqlDBPool._pool._connections, 1)

        self.mysql_db_pool.recycle_connection()
        self.assertEqual(MySqlDBPool._pool._connections, 0)

        with MySqlDBPool() as _:
            self.assertEqual(MySqlDBPool._pool._connections, 1)
            pass
        self.assertEqual(MySqlDBPool._pool._connections, 0)


if __name__ == '__main__':
    unittest.main()
