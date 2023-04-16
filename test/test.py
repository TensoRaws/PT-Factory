import os
import pathlib
from loguru import logger
from src.ptgenplus import PtGenPlus

projectPATH = pathlib.Path(os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

_encode_path = projectPATH / "assets" / "Kimetsu no Yaiba S04E01 2023 2160p B-Global WEB-DL x264 AAC-AnimeS@ADWeb.mp4"

if __name__ == "__main__":
    logger.add(projectPATH / "logs/log-{time}.log", encoding="utf-8")

    worker01 = PtGenPlus()
    worker01.create(str(projectPATH))

    print("如果不需要对比图，仅填写Encode路径或Source路径即可")
    worker01.bgm_douban_imdb_url = ""
    worker01.encode_path = _encode_path
    worker01.source_path = ""
    logger.info(str(worker01.get_config()))
    worker01.final_info_generate()
