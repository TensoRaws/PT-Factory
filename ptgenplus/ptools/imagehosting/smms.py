import sys
import requests
from loguru import logger
from tenacity import retry, wait_random, stop_after_delay, stop_after_attempt


@retry(wait=wait_random(min=3, max=5), stop=stop_after_delay(10) | stop_after_attempt(30))
@logger.catch
def upload_to_smms(proxy, pic_hosting_settings, image_path) -> str:
    files = {'smfile': open(image_path, 'rb')}
    smms_settings = pic_hosting_settings["smms"]
    logger.info("正在上传到sm.ms...")

    smms_headers = {
        "User-Agent"   : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/80.0.3987.149 Safari/537.36",
        "Authorization": smms_settings["APIKEY"]
    }

    if proxy["switch"]:
        proxies = {"http" : "socks5://" + proxy["ip_port"],
                   "https": "socks5://" + proxy["ip_port"]}
    else:
        proxies = None

    logger.info("headers: " + str(smms_headers))
    try:
        smms_response = requests.post(smms_settings["URL"], files=files, headers=smms_headers, proxies=proxies)
        smms_json = smms_response.json()
        if smms_json["code"] == "success":
            logger.info("上传成功，图片链接为：" + smms_json["data"]["url"])
            return '[url=' + smms_json['data']['page'] + '][img]' + smms_json['data']['url'] + '[/img][/url]'
        else:
            logger.error("上传失败，错误信息为：" + smms_json["message"])
            sys.exit(1)
    except Exception as e:
        logger.warning("上传失败，重试中" + str(e))
        raise e
