import os
import pathlib
import random
import sys
import cv2
import pyperclip
import yaml
from time import strftime, gmtime
from loguru import logger
from src.ptools import PTools


class PtGenPlus:
    def __init__(self,
                 project_path: str = "",
                 bgm_douban_imdb_url: str = "",
                 source_path: str = "",
                 encode_path: str = "",
                 proxy_settings=None,
                 pt_gen=None,
                 pic_hosting_settings=None,
                 torrent_settings=None,
                 upload_settings=None,
                 upload_logo=None,
                 mediainfo_settings=None,
                 ):
        self.project_path = project_path  # 项目路径
        self.bgm_douban_imdb_url = bgm_douban_imdb_url  # bgm，豆瓣，imdb详细url
        self.encode_path = encode_path  # Encode视频地址
        self.source_path = source_path  # 原视频地址
        self.output_stuff = ""  # 输出文件夹路径
        # 以下为config文件载入的参数
        self.proxy_settings = proxy_settings  # 代理设置
        self.pt_gen = pt_gen  # pt-gen设置
        self.pic_hosting_settings = pic_hosting_settings  # 图床上传设置
        self.torrent_settings = torrent_settings  # torrent设置
        self.upload_settings = upload_settings  # 上传设置
        self.upload_logo = upload_logo  # 上传logo
        self.mediainfo_settings = mediainfo_settings  # mediainfo格式设置

    @logger.catch
    def get_config(self, config_path: str = "") -> dict:
        if config_path == "":
            base_path = self.project_path
            file_path = os.path.abspath(os.path.join(base_path, "config.yaml"))  # 获取config文件路径
        else:
            file_path = config_path

        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            logger.error("Load config error: {}".format(e))
            sys.exit(1)

        return {
            "proxy-settings"      : config["proxy-settings"],
            "pt-gen"              : config["pt-gen"],
            "pic-hosting-settings": config["pic-hosting-settings"],
            "torrent-settings"    : config["torrent-settings"],
            "upload-settings"     : config["upload-settings"],
            "upload-logo"         : config["upload-logo"],
            "mediainfo-settings"  : config["mediainfo-settings"],
        }

    @logger.catch
    def create_from_dict(self, projectPATH: str, config: dict) -> None:
        self.project_path = projectPATH

        try:
            self.proxy_settings = config["proxy-settings"]
            self.pt_gen = config["pt-gen"]
            self.pic_hosting_settings = config["pic-hosting-settings"]
            self.torrent_settings = config["torrent-settings"]
            self.upload_settings = config["upload-settings"]
            self.upload_logo = config["upload-logo"]
            self.mediainfo_settings = config["mediainfo-settings"]
        except Exception as e:
            logger.error("Load config dict error: {}".format(e))
            sys.exit(1)

    @logger.catch
    def create(self, projectPATH: str) -> None:
        self.project_path = projectPATH

        try:
            config = self.get_config()
        except Exception as e:
            logger.error("Load config dict error: {}".format(e))
            sys.exit(1)

        self.proxy_settings = config["proxy-settings"]
        self.pt_gen = config["pt-gen"]
        self.pic_hosting_settings = config["pic-hosting-settings"]
        self.torrent_settings = config["torrent-settings"]
        self.upload_settings = config["upload-settings"]
        self.upload_logo = config["upload-logo"]
        self.mediainfo_settings = config["mediainfo-settings"]

    @logger.catch
    def final_info_generate(self):
        if self.encode_path != "":
            file_name = str(pathlib.PureWindowsPath(self.encode_path)).split("\\")[-1]
        else:
            file_name = str(pathlib.PureWindowsPath(self.source_path)).split("\\")[-1]
        file_name += "__final_info.txt"
        
        os.makedirs(
            os.path.join(self.project_path, "generate_stuff"),
            exist_ok=True
        )

        self.output_stuff = os.path.join(self.project_path, "generate_stuff")

        file_name = os.path.abspath(os.path.join(self.output_stuff, file_name))

        logger.info("Generate final info name: {}".format(file_name))

        self.proxy_settings["switch"] = True if PTools.check_proxy(self.proxy_settings) else False

        with open(file_name, "w", encoding="utf-8") as final_info:
            final_info.write(self.upload_settings["mini-essay"] + "\n")
            pt_gen_path = self.encode_path if self.encode_path != "" else self.source_path
            final_info.write(self.get_pt_gen_info(self.bgm_douban_imdb_url, self.proxy_settings, self.pt_gen["URL"],
                                                  self.pt_gen["APIKEY"], pt_gen_path))

        with open(file_name, "a", encoding="utf-8") as final_info:
            input_path = self.encode_path if self.encode_path != "" else self.source_path
            logo = self.upload_logo
            if logo["flag"]:
                final_info.write("\n\n" + "[quote][font=Courier New]" + logo["logo1"] + "\n")
            else:
                final_info.write("\n\n" + "[quote][font=Courier New]" + "\n")

            for i1 in self.get_media_info(input_path):
                final_info.write(i1)

            final_info.write("[/font][/quote]\n\n")

            # 固定内容
            if logo["flag"]:
                final_info.write(logo["logo2"] + "\n")
            final_info.write('[b] right click on the image and open it in a new tab to see the full-size one [/b]\n')

        if self.encode_path != "" and self.source_path != "":
            with open(file_name, "a", encoding="utf-8") as final_info:
                for i2 in self.get_screens():
                    final_info.write(i2)
        else:
            with open(file_name, "a", encoding="utf-8") as final_info:
                single_path = self.source_path if self.encode_path == "" else self.encode_path
                if not self.upload_settings["ffmpeg"]:
                    for i2 in self.get_screens_single(single_path):
                        final_info.write(i2)
                else:
                    for i2 in self.get_screens_single_ffmpeg(single_path):
                        final_info.write(i2)

        try:
            with open(file_name, "r", encoding="utf-8") as final_info:
                pyperclip.copy(final_info.read())
                logger.info("生成完毕！已复制到剪贴板")
        except Exception as e:
            logger.error(e)
            logger.error("复制失败，请手动打开txt文件")

        if self.torrent_settings["mk-or-not"]:
            torrent_config = self.torrent_settings
            torrent_path = self.encode_path if self.encode_path != "" else self.source_path
            torrent_path_0 = os.path.dirname(torrent_path)
            torrent_path_1 = os.path.dirname(torrent_path_0)
            print("当前制种目录0（默认回车）为：" + torrent_path_0)
            print("当前制种目录1为：" + torrent_path_1)
            flag = input("是否制作种子？对0/1目录制种~(0/1/N)：")
            if flag == "0" or flag == "":
                logger.info("制作种子目录0：{}".format(torrent_path_0))
                PTools.get_torrent(self.output_stuff, torrent_path_0, torrent_config)
            elif flag == "1":
                logger.info("制作种子目录1：{}".format(torrent_path_1))
                PTools.get_torrent(self.output_stuff, torrent_path_1, torrent_config)
            else:
                logger.info("未制作种子")

    @staticmethod
    @logger.catch
    def get_pt_gen_info(bgm_douban_imdb_url, proxy_settings, pt_gen_url, pt_gen_apikey, path):
        if bgm_douban_imdb_url == "":
            title = PTools.search_anidb(proxy_settings, path)
            bgm_douban_imdb_url = PTools.search_bgm(title, proxy_settings)

        return PTools.get_pt_gen_info(bgm_douban_imdb_url, proxy_settings, pt_gen_url, pt_gen_apikey)

    @logger.catch
    def get_media_info(self, input_path):
        return PTools.get_media_info(self.mediainfo_settings, input_path, self.upload_settings["encode-or-dl"],
                                     self.upload_settings["uploader-name"])

    @staticmethod
    @logger.catch
    def upload_to_pic_hosting(proxy_settings, pic_hosting_settings, image_path):
        return PTools.upload_to_pic_hosting(proxy_settings, pic_hosting_settings, image_path)

    @logger.catch
    def get_screens(self):
        cap_1 = cv2.VideoCapture(os.path.abspath(self.source_path))
        cap_2 = cv2.VideoCapture(os.path.abspath(self.encode_path))
        frames_num_1 = int(cap_1.get(7))
        frames_num_2 = int(cap_2.get(7))
        if frames_num_1 != frames_num_2:
            logger.warning("视频可能有问题，帧数相差" + str(frames_num_1 - frames_num_2))
            logger.warning('Source视频总帧数：' + str(frames_num_1))
            logger.warning('Encode视频总帧数：' + str(frames_num_2))
        # 这是按间隔取帧的参数，例如这里是5的话会把视频按时间轴从头到尾分为6段，去掉头段，取中间五段中的每段第一帧的前后的某个随机帧
        n = self.upload_settings["upload-pic-num"]
        frames_num_min = min(frames_num_1, frames_num_2)
        split_num = int(frames_num_min / (n + 1))  # 切分块的帧数
        output_dir = os.path.abspath(os.path.join(
            self.output_stuff, "Compare_Pics__" + str(pathlib.PureWindowsPath(self.encode_path)).split("\\")[-1]
        ))
        os.makedirs(output_dir, exist_ok=True)

        split_num_deal = split_num
        if self.upload_logo["flag"]:
            s_e_logo = self.upload_logo["logo3"] + "\n"
            pic_list = [s_e_logo]
        else:
            pic_list = []
        # 对比S-Encode logo

        for i in range(n):
            logger.info("截图上传中...( ˶º̬˶ )୨⚑...第" + str(i + 1) + "组，共有" + str(n) + "组")
            random_frame = random.randint(int(split_num / (-2)), int(split_num / 2))
            split_num_deal += random_frame
            logger.info("当前目标帧为" + str(split_num_deal))
            cap_1.set(cv2.CAP_PROP_POS_FRAMES, split_num_deal)
            cap_2.set(cv2.CAP_PROP_POS_FRAMES, split_num_deal)
            try:
                s, s_1 = cap_1.read()
                e, e_1 = cap_2.read()
                logger.debug("CV2读取成功")
            except Exception as e:
                logger.error(e)
                logger.error("CV2读取失败")
                sys.exit(1)
            path_s = os.path.abspath(os.path.join(
                output_dir, str(pathlib.PureWindowsPath(self.encode_path)).split("\\")[-1] + "__" +
                            str(split_num_deal) + '_source_' + '.jpg'
            ))
            path_e = os.path.abspath(os.path.join(
                output_dir, str(pathlib.PureWindowsPath(self.encode_path)).split("\\")[-1] + "__" +
                            str(split_num_deal) + '_encode_' + '.jpg'
            ))

            cv2.imencode('.jpg', s_1)[1].tofile(path_s)

            res_s = self.upload_to_pic_hosting(self.proxy_settings, self.pic_hosting_settings, path_s)

            pic_list.append(res_s + " ")

            cv2.imencode('.jpg', e_1)[1].tofile(path_e)

            res_e = self.upload_to_pic_hosting(self.proxy_settings, self.pic_hosting_settings, path_e)

            pic_list.append(res_e + "\n")

            split_num_deal -= random_frame
            split_num_deal += split_num

        return pic_list

    @logger.catch
    def get_screens_single(self, input_path):
        single_path = os.path.abspath(input_path)

        cap_single = cv2.VideoCapture(single_path)
        frames_num_single = int(cap_single.get(7))
        # 这是按间隔取帧的参数，例如这里是5的话会把视频按时间轴从头到尾分为6段，去掉头段，取中间五段中的每段第一帧的前后的某个随机帧
        n = self.upload_settings["upload-pic-num"]
        split_num = int(frames_num_single / (n + 1))  # 切分块的帧数
        output_dir = os.path.abspath(os.path.join(
            self.output_stuff, "Single_Pics__" + str(pathlib.PureWindowsPath(single_path)).split("\\")[-1]
        ))
        os.makedirs(output_dir, exist_ok=True)

        split_num_deal = split_num
        pic_list = []

        for i in range(n):
            logger.info("截图上传中...( ˶º̬˶ )୨⚑...第" + str(i + 1) + "组，共有" + str(n) + "组")
            random_frame = random.randint(int(split_num / (-2)), int(split_num / 2))
            split_num_deal += random_frame
            logger.info("当前目标帧为" + str(split_num_deal))
            cap_single.set(cv2.CAP_PROP_POS_FRAMES, split_num_deal)
            try:
                _, e_s_1 = cap_single.read()
                logger.debug("CV2读取成功")
            except Exception as e:
                logger.error(e)
                logger.error("CV2读取失败")
                sys.exit(1)
            path_s_or_e = os.path.abspath(os.path.join(
                output_dir, str(pathlib.PureWindowsPath(single_path)).split("\\")[-1] + "__" +
                            str(split_num_deal) + "__V__" + '.jpg'
            ))

            cv2.imencode('.jpg', e_s_1)[1].tofile(path_s_or_e)

            res_e_s = self.upload_to_pic_hosting(self.proxy_settings, self.pic_hosting_settings, path_s_or_e)

            pic_list.append(res_e_s + "\n")

            split_num_deal -= random_frame
            split_num_deal += split_num

        return pic_list

    @logger.catch
    def get_screens_single_ffmpeg(self, input_path):
        single_path = os.path.abspath(input_path)

        cap_single = cv2.VideoCapture(single_path)
        frames_num_single = int(cap_single.get(7))
        frames_rate_single = int(cap_single.get(5))  # 帧速率

        duration = frames_num_single / frames_rate_single  # 帧速率/视频总帧数

        n = self.upload_settings["upload-pic-num"]
        split_time = int(duration / (n + 1))  # 切分块的时间
        output_dir = os.path.abspath(os.path.join(
            self.output_stuff, "Single_Pics__" + str(pathlib.PureWindowsPath(single_path)).split("\\")[-1]
        ))
        os.makedirs(output_dir, exist_ok=True)

        split_time_deal = split_time
        pic_list = []
        pic_time_list = []

        for time in range(n):
            random_time = random.randint(int(split_time / (-2)), int(split_time / 2))
            split_time_deal += random_time
            pic_time_list.append(strftime("%H:%M:%S", gmtime(split_time_deal)))
            split_time_deal -= random_time
            split_time_deal += split_time
        logger.info("待获取的时间：" + str(pic_time_list))

        ffmpeg_config = "ffmpeg -ss \"{}\" -i \"{}\" -vframes 1 \"{}\" "

        for t in pic_time_list:
            logger.info("截取中，当前为：" + str(t))
            path_s_or_e = os.path.abspath(os.path.join(
                output_dir, str(pathlib.PureWindowsPath(single_path)).split("\\")[-1] + "__" +
                            t.replace(":", "_") + "__V__" + '.jpg'
            ))
            ffmpeg_encode = ffmpeg_config.format(t, single_path, path_s_or_e)
            print(ffmpeg_encode)
            is_run = os.system(ffmpeg_encode)
            if is_run != 0:
                logger.error("Maybe ffmpeg got error, Please check it")

            res_e_s = self.upload_to_pic_hosting(self.proxy_settings, self.pic_hosting_settings, path_s_or_e)
            pic_list.append(res_e_s + "\n")

        return pic_list
