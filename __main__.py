import argparse
import os
import sys
from loguru import logger
from ptgenplus.ptgenplus import PtGenPlus

logger.add(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/logs/log-{time}.log"),
           encoding="utf-8")

worker01 = PtGenPlus.create()

parser = argparse.ArgumentParser()
parser.description = "如果不需要对比图，仅填写Encode路径或Source路径即可"
parser.add_argument("-u", "--URL", help="豆瓣，bangumi,IMDB的详细URL", type=str)
parser.add_argument("-e", "--ENCODE", help="Encode资源路径", type=str)
parser.add_argument("-s", "--SOURCE", help="Source资源路径", type=str)
args = parser.parse_args()

worker01.bgm_douban_imdb_url = args.URL if args.URL is not None else ""
worker01.encode_path = args.ENCODE if args.ENCODE is not None else ""
worker01.source_path = args.SOURCE if args.SOURCE is not None else ""

if worker01.bgm_douban_imdb_url == "" and worker01.encode_path == "" and worker01.source_path == "":
    parser.print_help()
    sys.exit(0)
logger.info(str(PtGenPlus.get_config()))
worker01.final_info_generate()
