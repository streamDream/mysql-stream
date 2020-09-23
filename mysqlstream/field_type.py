# brief: 数据字段类型
from .en_decoder import TextEnDecoder, DatetimeEnDecoder


class FieldType:
    """
    数据库字段基类
    """
    def __init__(self, name, column_type, primary_key, default, en_decoder):
        self.name = name  # 数据表的列名
        self.column_type = column_type  # 列类型
        self.primary_type = primary_key   # 是否是主键
        self.default = default  # 列的默认值
        self.en_decoder = en_decoder  # 编解码类名


class StringType(FieldType):
    """
    char，varchar字段类型
    """
    def __init__(self, name=None, column_type='varchar(32)', primary_key=False, default=None, en_decoder=None):
        super(StringType, self).__init__(name, column_type, primary_key, default, en_decoder)


class IntegerType(FieldType):
    """
    int，tinyint字段类型
    """
    def __init__(self, name=None, column_tye='int(32)', primary_key=False, default=None, en_decoder=None):
        super(IntegerType, self).__init__(name, column_tye, primary_key, default, en_decoder)


class TextType(FieldType):
    """
    text字段类型
    """
    def __init__(self, name=None, column_type='text', primary_key=False, default=None, en_decoder=TextEnDecoder):
        super(TextType, self).__init__(name, column_type, primary_key, default, en_decoder)


class DatetimeType(FieldType):
    """
    timestamp，datetime字段类型
    """
    def __init__(self, name=None, column_type='datetime', primary_key=False,
                 default='0000-00-00 00:00:00', en_decoder=DatetimeEnDecoder):
        super(DatetimeType, self).__init__(name, column_type, primary_key, default, en_decoder)
