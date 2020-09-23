# brief: 自定义的编解码器基类
import json
from datetime import datetime


class EnDecoder:

    @classmethod
    def encode(cls, value):
        """
        编码方法
        """
        raise NotImplemented

    @classmethod
    def decode(cls, value):
        """
        解码方法
        """
        raise NotImplemented


class TextEnDecoder(EnDecoder):

    @classmethod
    def encode(cls, value):
        return json.dumps(value, ensure_ascii=False)

    @classmethod
    def decode(cls, value):
        return json.loads(value)


class DatetimeEnDecoder(EnDecoder):

    @classmethod
    def encode(cls, value):
        return value

    @classmethod
    def decode(cls, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value