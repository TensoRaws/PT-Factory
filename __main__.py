import argparse
import os
import pathlib
import sys
from loguru import logger
from src.ptgenplus import PtGenPlus

# python -m PyInstaller -F -n ptf -i assets/favicon.icon __main__.py
if getattr(sys, 'frozen', False):
    # frozen
    projectPATH = pathlib.Path(os.path.abspath(os.path.dirname(sys.executable)))
else:
    # unfrozen
    projectPATH = pathlib.Path(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))

logger.add(projectPATH / "logs/log-{time}.log", encoding="utf-8")

worker01 = PtGenPlus()

parser = argparse.ArgumentParser()
parser.description = "如果不需要对比图，仅填写-e或-s参数即可  ||  对于二次元番剧电影，可尝试不指定-u参数直接搜索"
parser.add_argument("-u", "--URL", help="豆瓣，bangumi，IMDB的详细URL", type=str)
parser.add_argument("-e", "--ENCODE", help="Encode资源路径", type=str)
parser.add_argument("-s", "--SOURCE", help="Source资源路径", type=str)
args = parser.parse_args()

worker01.bgm_douban_imdb_url = args.URL if args.URL is not None else ""
worker01.encode_path = args.ENCODE if args.ENCODE is not None else ""
worker01.source_path = args.SOURCE if args.SOURCE is not None else ""

if worker01.bgm_douban_imdb_url == "" and worker01.encode_path == "" and worker01.source_path == "":
    parser.print_help(sys.stderr)
    sys.exit(0)

worker01.create(str(projectPATH))

logger.info(str(worker01.get_config()))
worker01.final_info_generate()
