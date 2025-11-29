#统一日志模块 (src/core/logger.py)

import logging
import os
import sys


def setup_logger(name, log_file=None, level=logging.INFO):
    """配置并返回一个 logger 实例"""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if not logger.handlers:
        # 1. 输出到控制台
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # 2. 输出到文件 (如果有路径)
        if log_file:
            # 自动创建 logs 文件夹
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
