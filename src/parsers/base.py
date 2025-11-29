# src/parsers/base.py (定义标准)
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_data):
        """所有 Parser 必须实现这个方法，输入原始数据，输出 DataFrame"""
        pass
