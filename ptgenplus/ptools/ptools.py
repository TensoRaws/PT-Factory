import os
import pathlib
import string
from torrentool.torrent import Torrent
from .imagehosting.smms import *
from .mediainfo import *
from lxml import etree


class PTools:
    @staticmethod
    @logger.catch
    def check_proxy(proxy: dict) -> bool:
        if not proxy["switch"]:
            logger.info("Not using proxy")
            return False
        try:
            proxies = {
                "http" : "socks5://" + proxy["ip_port"],
                "https": "socks5://" + proxy["ip_port"]
            }
            requests.get("https://www.baidu.com", proxies=proxies)
            logger.info("Proxy check success, using proxy")
            return True
        except Exception as e:
            logger.warning(e)
            logger.warning("Proxy check failed, not using proxy")
            return False

    @staticmethod
    @logger.catch
    @retry(wait=wait_random(min=2, max=4), stop=stop_after_delay(30) | stop_after_attempt(10))
    def get_pt_gen_info(bgm_douban_imdb_url: str, proxy: dict, pt_gen_url: str, pt_gen_api: str) -> str:
        if proxy["switch"]:
            pt_gen_proxy = {
                "http" : "socks5://" + proxy["ip_port"],
                "https": "socks5://" + proxy["ip_port"]
            }
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
            if pt_gen_response["success"]:
                logger.info("获取ptgen信息成功")
                return pt_gen_response["format"]
            else:
                logger.error("未查询到信息，ptgen返回结果：" + str(pt_gen_response))
                sys.exit(1)
        except Exception as e:
            logger.warning("获取ptgen信息失败，正在重试...请检查api，url和网络连接")
            raise e

    @staticmethod
    @logger.catch
    @retry(wait=wait_random(min=2, max=4), stop=stop_after_delay(30) | stop_after_attempt(10))
    def search_bgm(title: str, proxy: dict) -> str:
        if proxy["switch"]:
            search_bgm_proxy = {
                "http" : "socks5://" + proxy["ip_port"],
                "https": "socks5://" + proxy["ip_port"]
            }
        else:
            search_bgm_proxy = None

        logger.info("正在搜索bangumi...")
        url = "https://bgm.tv/subject_search/" + title
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.149 Safari/537.36"
        }
        p = {
            "cat": 2
        }

        try:
            req_res = requests.get(url=url, params=p, proxies=search_bgm_proxy, headers=headers).text
        except Exception as e:
            logger.warning(e)
            logger.warning("网络请求失败，重试中")
            raise e

        try:
            res = etree.HTML(req_res).xpath(
                '//*[@id="browserItemList"]//li[contains(@id, "item")][1]/a/@href')[0]
        except Exception as e:
            logger.warning(e)
            logger.warning("未查询到bgm信息，请手动输入")
            res = input("手动填入bgm/douban/idmb地址：")
            logger.info(res)
            return res
        res = "https://bgm.tv" + res
        logger.info(res)
        return res

    @staticmethod
    @logger.catch
    @retry(wait=wait_random(min=2, max=4), stop=stop_after_delay(30) | stop_after_attempt(10))
    def search_anidb(proxy: dict, path: str) -> str:
        # 清洗特殊符号
        path = str(pathlib.PureWindowsPath(path)).split("\\")[-1]
        for i in path:
            if i in string.punctuation:
                path = path.replace(i, " ")

        logger.info("搜索Anidb中...动画名为" + path)
        if proxy["switch"]:
            get_bangmumi_url_proxy = {
                "http" : "socks5://" + proxy["ip_port"],
                "https": "socks5://" + proxy["ip_port"]
            }
        else:
            get_bangmumi_url_proxy = None
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.149 Safari/537.36"
        }
        p = {
            "adb.search": path,
            "do.search" : 1
        }
        url = "https://anidb.net/search/anime/"
        try:
            req_title_url = requests.get(url=url, params=p, headers=headers, proxies=get_bangmumi_url_proxy).text
        except Exception as e:
            logger.warning(e)
            logger.warning("网络请求失败，重试中")
            raise e
        # 获取详情界面url
        title_url = ""
        try:
            title_url = etree.HTML(req_title_url).xpath(
                '//*[@id="layout-main"]/div[1]/div[2]/table/tbody/tr[1]/td[4]/a/@href')[0]
        except Exception as e:
            logger.warning(e)
            logger.info("未查询到ANIDB结果")
            return "未查询到ANIDB结果"

        title_url = "https://anidb.net" + title_url
        logger.info("title_url: " + title_url)
        try:
            req_title_name = requests.get(url=title_url, headers=headers, proxies=get_bangmumi_url_proxy).text
        except Exception as e:
            logger.warning(e)
            logger.warning("网络请求失败，重试中")
            raise e
        # 优先使用日语标题
        try:
            title_name = etree.HTML(req_title_name).xpath(
                '//*[@id="tab_1_pane"]/div/table/tbody/tr[3]/td/label/text()')[0]
        except Exception as e:
            logger.warning(e)
            logger.warning("标题#3不存在，尝试获取标题#2")
            try:
                title_name = etree.HTML(req_title_name).xpath(
                    '//*[@id="tab_1_pane"]/div/table/tbody/tr[2]/td/label/text()')[0]
            except Exception as e:
                logger.warning(e)
                logger.warning("标题#2不存在，尝试获取主标题")
                title_name = etree.HTML(req_title_name).xpath(
                    '//*[@id="tab_1_pane"]/div/table/tbody/tr[1]/td/span/text()')[0]
        # 清洗特殊符号
        for item in title_name:
            if item in string.punctuation:
                title_name = title_name.replace(item, " ")

        logger.info("获取title成功： " + title_name)
        return title_name

    @staticmethod
    @logger.catch
    def get_media_info(mediainfo_settings: int, file_path: str, encode_or_dl: str, uploader_name: str) -> list:
        choose_media_info = {
            0: lambda a, b, c: get_media_info_0(a, b, c),
            1: lambda a, b, c: get_media_info_1(a, b, c)
        }

        return choose_media_info[mediainfo_settings](file_path, encode_or_dl, uploader_name)

    # 返回图床BBcode
    @staticmethod
    @logger.catch
    def upload_to_pic_hosting(proxy: dict, pic_hosting_settings: dict, image_path: str) -> str:
        choose_pic_hosting = {
            0: lambda a, b, c: upload_to_smms(a, b, c)
        }

        return choose_pic_hosting[pic_hosting_settings["id"]](proxy, pic_hosting_settings, image_path)

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
        output_path = os.path.abspath(os.path.join(
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
