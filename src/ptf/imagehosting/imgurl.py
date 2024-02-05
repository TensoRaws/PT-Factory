import sys

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_random


@logger.catch
@retry(wait=wait_random(min=3, max=5), stop=stop_after_delay(10) | stop_after_attempt(30))
def upload_to_imgurl(proxy, pic_hosting_settings, image_path) -> str | None:  # type: ignore
    files = {"file": open(image_path, "rb")}
    imgurl_settings = pic_hosting_settings["imgurl"]
    logger.info("正在上传到imgurl...")

    imgurl_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Safari/537.36",
    }

    p = {"uid": imgurl_settings["UID"], "token": imgurl_settings["TOKEN"]}

    if proxy["switch"]:
        proxies = {"http": "socks5://" + proxy["ip_port"], "https": "socks5://" + proxy["ip_port"]}
    else:
        proxies = None

    try:
        imgurl_response = requests.post(
            imgurl_settings["URL"], data=p, files=files, headers=imgurl_headers, proxies=proxies
        )
        imgurl_json = imgurl_response.json()
        print(imgurl_json)
        if imgurl_json["code"] == 200:
            logger.info("上传成功，图片链接为：" + imgurl_json["data"]["url"])
            return "[img]" + imgurl_json["data"]["url"] + "[/img]"
        else:
            logger.error("上传失败，错误信息为：" + imgurl_json["msg"])
            sys.exit(1)
    except Exception as e:
        logger.warning("上传失败，重试中" + str(e))
        raise e
