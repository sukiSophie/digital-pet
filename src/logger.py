import logging
import sys
import os

def setup_logging(log_file="pet.log"):
    """配置全局日志系统，并将标准输出重定向到日志文件"""
    
    # 获取日志文件的绝对路径（放在项目根目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(project_root, log_file)

    # 创建日志格式
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(log_format)

    # 根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # 为了将 print 语句也捕获到日志中，我们可以自定义一个流对象来重定向 sys.stdout/stderr
    class StreamToLogger:
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level
            self.linebuf = ''

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.level, line.rstrip())

        def flush(self):
            pass

    sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
    sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)

    logging.info(f"--- 日志系统初始化成功，日志文件：{log_path} ---")

# 获取各模块使用的 logger
def get_logger(name):
    return logging.getLogger(name)
