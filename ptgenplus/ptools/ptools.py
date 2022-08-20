import os
import pathlib
from torrentool.torrent import Torrent
from .imagehosting.smms import *
from .mediainfo import *


class PTools:
    @staticmethod
    @retry(wait=wait_random(min=2, max=4), stop=stop_after_delay(30) | stop_after_attempt(10))
    @logger.catch
    def get_pt_gen_info(bgm_douban_imdb_url: str, proxy: dict, pt_gen_url: str, pt_gen_api: str) -> str:
        if PTools.check_proxy(proxy):
            pt_gen_proxy = {"http" : "socks5://" + proxy["ip_port"],
                            "https": "socks5://" + proxy["ip_port"]}
        else:
            pt_gen_proxy = None

        logger.info("正在获取ptgen信息...")
        dict_pt_gen_params = {
            "url"   : bgm_douban_imdb_url,
            "apikey": pt_gen_api
        }

        logger.info("ptgen params: {}".format(dict_pt_gen_params))
        try:
            pt_gen_response = requests.get(url=pt_gen_url, params=dict_pt_gen_params, proxies=pt_gen_proxy).json()
            if "error" in pt_gen_response and pt_gen_response["error"] is not None:
                logger.error("ptgen API填写错误，请检查 || " + str(pt_gen_response))
                sys.exit(1)
            if pt_gen_response["success"]:
                logger.info("获取ptgen信息成功")
                return pt_gen_response["format"]
            else:
                logger.error("未查询到信息，ptgen返回结果：" + str(pt_gen_response))
                sys.exit(1)
        except Exception as e:
            logger.warning("获取ptgen信息失败，正在重试...请检查url和网络连接")
            raise e

    @staticmethod
    @logger.catch
    def get_media_info(mediainfo_settings: int, file_path: str, encode_or_dl: str, uploader_name: str) -> list:
        choose_media_info = {
            0: lambda a, b, c: get_media_info_0(a, b, c)
        }

        return choose_media_info[mediainfo_settings](file_path, encode_or_dl, uploader_name)

    @staticmethod
    @logger.catch
    def get_torrent(output_path: str, mktorrent_path: str, config: dict):
        try:
            torrent_config = config
            logger.info("获取torrent配置文件成功")
        except Exception as e:
            logger.error(e)
            logger.error("获取torrent配置文件失败，请检查配置文件是否正确")
            sys.exit(1)
        output_path =  os.path.abspath(os.path.join(
            output_path, str(pathlib.PureWindowsPath(mktorrent_path)).split("\\")[-1] + ".torrent"
        ))

        logger.info("输出路径：" + output_path)

        new_torrent = Torrent.create_from(mktorrent_path)
        logger.info("生成torrent文件成功")
        new_torrent.private = True
        new_torrent.name = str(pathlib.PureWindowsPath(mktorrent_path)).split("\\")[-1]
        new_torrent.announce_urls = torrent_config["announce-urls"]
        new_torrent.comment = torrent_config["comment"]
        new_torrent.created_by = torrent_config["created-by"]
        logger.info(torrent_config)
        new_torrent.to_file(output_path)
        logger.info("生成torrent文件成功")

    @staticmethod
    @logger.catch
    def check_proxy(proxy: dict) -> bool:
        if not proxy["switch"]:
            logger.info("Not using proxy")
            return False
        try:
            proxies = {"http" : "socks5://" + proxy["ip_port"],
                       "https": "socks5://" + proxy["ip_port"]}
            requests.get("https://www.baidu.com", proxies=proxies)
            logger.info("Proxy check success, using proxy")
            return True
        except Exception as e:
            logger.warning(e)
            logger.warning("Proxy check failed, not using proxy")
            return False

    # 返回图床BBcode
    @staticmethod
    @logger.catch
    def upload_to_pic_hosting(proxy: dict, pic_hosting_settings: dict, image_path: str) -> str:
        proxy["switch"] = True if PTools.check_proxy(proxy) else False

        choose_pic_hosting = {
            0: lambda a, b, c: upload_to_smms(a, b, c)
        }

        return choose_pic_hosting[pic_hosting_settings["id"]](proxy, pic_hosting_settings, image_path)