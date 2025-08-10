import logging
import os
import sys
from datetime import datetime
from functools import lru_cache
from logging.handlers import TimedRotatingFileHandler

import git

# 로그 폴더 생성
repo = git.Repo(search_parent_directories=True)
log_dir = os.path.join(repo.working_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# 오늘 날짜 기반 파일명
today_str = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(log_dir, f"{today_str}.log")

# 로거 생성
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 포맷
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# 콘솔 핸들러
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# 시간 기반 파일 핸들러 (매일 자정마다 새 파일 생성)
file_handler = TimedRotatingFileHandler(filename=log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


# 날짜가 바뀌면 파일명을 새 날짜로 변경
def custom_namer(default_name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"{date_str}.log")


file_handler.namer = custom_namer

# 로거에 핸들러 추가
logger.addHandler(console_handler)
logger.addHandler(file_handler)


@lru_cache
def get_logger():
    return logger


def test():
    logger.info("test")


if __name__ == "__main__":
    test()
