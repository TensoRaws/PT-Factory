import os
from loguru import logger
from ptgenplus.ptgenplus import PtGenPlus

if __name__ == "__main__":
    logger.add(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/logs/log-{time}.log"),
               encoding="utf-8")

    worker01 = PtGenPlus.create()

    print("如果不需要对比图，仅填写Encode路径或Source路径即可")
    worker01.bgm_douban_imdb_url = input("请输入豆瓣，bangumi，IMDB资源详情界面的url：")
    worker01.encode_path = input("请输入Encode资源的路径：")
    worker01.source_path = input("请输入Source资源的路径：")
    logger.info(str(PtGenPlus.get_config()))
    worker01.final_info_generate()
