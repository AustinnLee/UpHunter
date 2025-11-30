#定义 Fetcher 接口规范 (src/fetchers/base.py)

from abc import ABC, abstractmethod


class BaseFetcher(ABC):
    """Fetcher 抽象基类"""

    @abstractmethod
    def fetch(self, url, **kwargs):
        """所有 Fetcher 必须实现 fetch 方法"""
        pass
