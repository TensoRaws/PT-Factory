import os
from typing import List

import pymediainfo
from loguru import logger


@logger.catch
def get_media_info(input_path: str, encode_or_dl: str, uploader_name: str) -> List[str]:
    logger.info("生成完整PYMediainfo中...: {}".format(input_path))
    write_path = os.path.abspath(input_path)
    encode_media_info = pymediainfo.MediaInfo.parse(write_path, output="YAML")
    return [encode_media_info]
