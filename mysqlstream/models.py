# brief: 数据库的model类
import re
from .field_type import FieldType
from .mysql_executor import MysqlExecutor


class ModelMetaclass(type):

    def __new__(mcs, name, base_tuple, attrs):
        if 'Model' == name:  # 不对修改基类
            return type.__new__(mcs, name, base_tuple, attrs)

        # 如果不定义，则使用类名中大写字母换成下划线和小写的方式
        table_name = attrs.get('__table__', None) or re.sub("[A-Z]", lambda x: "_" + x.group(0).lower(), name)

        column2attr = {}  # 列名存和属性名的映射
        column2field_obj = {}  # 列名和属性对象值的映射
        columns_without_primary_key = []  # 不包括主键的所有列名
        primary_key = None  # 主键列名
        for attr, v in attrs.items():
            if not isinstance(v, FieldType):
                continue

            column = attr
            if None is not v.name:  # 判断是否自定义了列名
                column = v.name
            column2attr[column] = attr
            column2field_obj[column] = v

            # 判断主键是否重复
            if v.primary_type:
                if primary_key:
                    raise Exception(f'More than one primary key in Model:<{name}>')
                primary_key = column
            else:
                columns_without_primary_key.append(column)
        if not primary_key:
            raise Exception(f'Primary key not found in Model:<{name}>')

        # 将列相关的attr删除
        for f in column2attr.values():
            attrs.pop(f, None)

        all_columns = '%s,%s' % (primary_key, ','.join(columns_without_primary_key))
        values_args = ','.join(["%s" for i in range(len(columns_without_primary_key) + 1)])
        update_args = ','.join([f"{k}=%s" for k in columns_without_primary_key])
        attrs['__column2attr__'] = column2attr
        attrs['__column2field_obj__'] = column2field_obj
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__columns_without_primary_key__'] = columns_without_primary_key
        attrs['__get__'] = """select {all_columns} from {table_name} 
                                where {primary_key}=%s""".format(primary_key=primary_key,
                                                                 all_columns=all_columns,
                                                                 table_name=table_name)

        attrs['__select__'] = """select {all_columns} from {table_name}""".format(all_columns=all_columns,
                                                                                  table_name=table_name)

        attrs['__insert__'] = """insert into {table_name} ({all_columns})
                                    value({values_args})""".format(table_name=table_name,
                                                                   all_columns=all_columns,
                                                                   values_args=values_args)

        attrs['__update__'] = """update {table_name} set {update_args} 
                                    where {primary_key}=%s""".format(table_name=table_name,
                                                                     update_args=update_args,
                                                                     primary_key=primary_key)
        attrs['__delete__'] = """delete from {table_name} 
                                    where {primary_key}=%s""".format(table_name=table_name,
                                                                     primary_key=primary_key)
        return type.__new__(mcs, name, base_tuple, attrs)


class Model(dict, metaclass=ModelMetaclass):  # 继承自 dict ！！！

    def __init__(self, **kwargs):
        # 调用父类的__init__
        super(Model, self).__init__(**kwargs)

    def __repr__(self):
        """
        打印出所有的attrs
        """
        lines = []
        for column, attr in self.__column2attr__.items():
            v = getattr(self, attr)
            lines.append(f'{attr}:{v}')
        return ','.join(lines)

    def __getattr__(self, item):
        """
        getattr调用的具体方法
        """
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"""Model object has no attribute:<{item}>""")

    def __setattr__(self, key, value):
        """
        赋值方法
        """
        self[key] = value

    def _decode(self, column, value):
        """
        使用指定的解码方法解码
        """
        field = self.__column2field_obj__[column]
        if field.en_decoder:  # 指定了解码器时的操作
            # print('..... begin ', value)
            value = field.en_decoder.decode(value)
            # print('..... end', value)
        return value

    def _encode(self, column, value):
        """
        编码列的值
        """
        obj = self.__column2field_obj__[column]
        if value is None:  # 未设置值，则使用默认值
            if None is not obj.default:
                value = obj.default() if callable(obj.default) else obj.default
            else:
                raise ValueError(f'Value of column:<column> is not found !')

        if obj.en_decoder:
            value = obj.en_decoder.encode(value)  # 调用编码器
        return value

    def _row2obj(self, row):
        """
        将单行转成对象
        """
        if not row:
            return None

        kwargs = {}
        cls = self.__class__
        for column, attr in self.__column2attr__.items():
            v = row[column]
            kwargs[attr] = self._decode(column, v)
        return cls(**kwargs)

    def _db_value_of_column(self, column):
        """
        根据列名获取该列的值
        """
        attr = self.__column2attr__[column]
        value = None
        try:
            value = getattr(self, attr)  # 获取到对象属性的值
        except AttributeError:
            pass
        return self._encode(column, value)

    def query_all(self, where=None, args=None, **kwargs):
        """
        指定查询条件和排序，分页等搜索
        """
        sql_elements = [self.__select__]
        if where:
            sql_elements.append('where')
            sql_elements.append(where)
        if None is args:
            args = []

        order_by = kwargs.get('order_by')
        if order_by:
            sql_elements.append('order by')
            sql_elements.append(order_by)

        limit = kwargs.get('limit', None)
        if limit is not None:
            sql_elements.append('limit')
            if isinstance(limit, int):
                sql_elements.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql_elements.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError(f"limit:{limit} is incorrect !")
        sql = ' '.join(sql_elements)
        rows = MysqlExecutor.query_multi_rows(sql, args)
        return [self._row2obj(row) for row in rows]

    def count_of_rows(self, column, where=None, args=None):
        """
        获取指定查询条件的行数
        """
        sql = ["""select count({column}) as total from {table}""".format(column=column, table=self.__table__)]
        if None is not where:
            sql.append('where')
            sql.append(where)
        sql = ' '.join(sql)
        row = MysqlExecutor.query_one_row(sql, args)
        if not row:
            return 0
        return row['total']

    def save(self):
        """
        保存
        """
        args = [self._db_value_of_column(self.__primary_key__)]
        args.extend(list(map(self._db_value_of_column, self.__columns_without_primary_key__)))
        return MysqlExecutor.execute(self.__insert__, args)

    def delete(self):
        """
        删除主键对应的行
        """
        args = [self._db_value_of_column(self.__primary_key__)]
        return MysqlExecutor.execute(self.__delete__, args)

    def update(self):
        """
        更新主键对应的行
        """
        args = list(map(self._db_value_of_column, self.__columns_without_primary_key__))
        args.append(self._db_value_of_column(self.__primary_key__))
        return MysqlExecutor.execute(self.__update__, args)

    def get(self, pk):
        """
        获取指定主键值的行
        """
        row = MysqlExecutor.query_one_row(self.__get__, pk)
        return self._row2obj(row)
