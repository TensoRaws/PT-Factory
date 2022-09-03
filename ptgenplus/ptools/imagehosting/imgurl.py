import sys
import requests
from loguru import logger
from tenacity import retry, wait_random, stop_after_delay, stop_after_attempt


@logger.catch
@retry(wait=wait_random(min=3, max=5), stop=stop_after_delay(10) | stop_after_attempt(30))
def upload_to_imgurl(proxy, pic_hosting_settings, image_path) -> str:
    files = {'file': open(image_path, 'rb')}
    imgurl_settings = pic_hosting_settings["imgurl"]
    logger.info("正在上传到imgurl...")

    imgurl_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/80.0.3987.149 Safari/537.36",
    }

    p = {
        "uid"  : imgurl_settings["UID"],
        "token": imgurl_settings["TOKEN"]
    }

    if proxy["switch"]:
        proxies = {"http" : "socks5://" + proxy["ip_port"],
                   "https": "socks5://" + proxy["ip_port"]}
    else:
        proxies = None

    try:
        imgurl_response = requests.post(imgurl_settings["URL"], data=p, files=files, headers=imgurl_headers,
                                        proxies=proxies)
        imgurl_json = imgurl_response.json()
        print(imgurl_json)
        if imgurl_json["code"] == 200:
            logger.info("上传成功，图片链接为：" + imgurl_json["data"]["url"])
            return '[img]' + imgurl_json['data']['url'] + '[/img]'
        else:
            logger.error("上传失败，错误信息为：" + imgurl_json["msg"])
            sys.exit(1)
    except Exception as e:
        logger.warning("上传失败，重试中" + str(e))
        raise e


# if __name__ == "__main__":
#     proxy = {
#         "switch" : False,  # boolean || Enable proxy or not
#         # socks5 proxy, 使用前请先配置好socks5代理, switch为true时检测其是否有效
#         "ip_port": "localhost:11223"  # string  || Proxy host
#     }
#     s = {
#         "imgurl": {
#             "TOKEN": "2732bf8ced8bdf253665b9cb58b312c9",  # String  || The TOKEN of the imgurl server
#             "UID"  : "ee7baa81c3229235e4392bb523891a52",  # String  || The UID of the imgurl server
#             "URL"  : "https://www.imgurl.org/api/v2/upload"  # String  || The URL of the imgurl server
#         }
#     }
#
#     img = "C:\\Users\\haiqu\\Desktop\\test\\photo_2021-06-05_04-50-01.jpg"
#
#     aaa = upload_to_imgurl(proxy, s, img)
#     print("dfsf")
#     print(aaa)
