# brief:


class TestConfig:
    _mysql_cfg = dict(
        host='',
        port=3306,
        username='chong',
        password=''
    )

    @classmethod
    def cfg_for_mysql_db_pool(cls):
        return cls._mysql_cfg


"""
CREATE TABLE `t_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `age` int(3) NOT NULL,
  `urls` text,
  `create_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
"""