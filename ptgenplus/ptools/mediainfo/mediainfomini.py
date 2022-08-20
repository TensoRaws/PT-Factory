import json
import os
import pathlib
import time
import pymediainfo
from loguru import logger


@logger.catch
def get_media_info(input_path: str, encode_or_dl: str, uploader_name: str) -> list:
    logger.info("生成Mediainfo-mini中...: {}".format(input_path))
    write_info_list = []
    write_path = os.path.abspath(input_path)
    encode_media_info = pymediainfo.MediaInfo.parse(write_path, output="JSON")
    encode_tracks = json.loads(encode_media_info)["media"]["track"]

    write_info_list.append(
        "\n" + "RELEASE.NAME........: " +
        str(pathlib.PureWindowsPath(write_path)).split("\\")[-1])
    write_info_list.append(
        "\n" + "RELEASE.DATE........: " +
        time.strftime("%Y-%m-%d", time.localtime()))

    try:
        file_size = encode_tracks[0]["FileSize_String"]
    except Exception as e:
        logger.warning(e)
        file_size = encode_tracks[0]["FileSize"]
        file_size = round(int(file_size) / (1024 * 1024), 2)
        if file_size > 1000:
            file_size = round(file_size / 1024, 2)
            file_size = str(file_size) + " GiB"
        else:
            file_size = str(file_size) + " MiB"

    write_info_list.append("\n" + "RELEASE.SIZE........: " + file_size)

    try:
        v_format = encode_tracks[0]["Format"]
    except Exception as e:
        logger.warning(e)
        v_format = "未知"

    write_info_list.append("\n" + "RELEASE.FORMAT......: " + v_format)

    try:
        overallbitrate = encode_tracks[0]["OverallBitRate_String"]
    except Exception as e:
        logger.warning(e)
        try:
            overallbitrate = encode_tracks[0]["OverallBitRate"]
            overallbitrate = round(int(overallbitrate) / 1000, 2)
            if overallbitrate > 10000:
                overallbitrate = round(overallbitrate / 1000, 2)
                if overallbitrate > 1000:
                    overallbitrate = round(overallbitrate / 1000, 2)
                    overallbitrate = str(overallbitrate) + " Gb/s"
                else:
                    overallbitrate = str(overallbitrate) + " Mb/s"
            else:
                overallbitrate = str(overallbitrate) + " kb/s"
        except Exception as e:
            logger.warning(e)
            overallbitrate = "未知"

    write_info_list.append("\n" + "OVERALL.BITRATE.....: " + overallbitrate)
    # 写视频轨参数
    video_track_id = 0
    try:
        for video_track_index, video_track in enumerate(encode_tracks):
            if video_track["@type"] == "Video":
                write_info_list.append(
                    "\n" + "RESOLUTION..........: " +
                    encode_tracks[video_track_index]["Width"] + "x" +
                    encode_tracks[video_track_index]["Height"])
                write_info_list.append(
                    "\n" + "BIT.DEPTH...........: " +
                    encode_tracks[video_track_index]["BitDepth"] + " bits")
                write_info_list.append(
                    "\n" + "FRAME.RATE..........: " +
                    encode_tracks[video_track_index]["FrameRate"] + " FPS")
                write_info_list.append(
                    "\n" + "VIDEO...............: " +
                    encode_tracks[video_track_index]["Format"] + ", " +
                    encode_tracks[video_track_index]["Format_Profile"])
                video_track_id += 1
    except Exception as e:
        logger.warning(e)
        logger.warning("异常的视频轨")
    if video_track_id != 1:
        logger.warning("可能存在多条视频轨道或无视频轨，请检查")
    # 写音轨参数
    audio_track_id = 1
    try:
        for audio_track_index, audio_track in enumerate(encode_tracks):
            if audio_track["@type"] == "Audio":
                write_info_list.append("\n" + "AUDIO#" + str(audio_track_id).zfill(2) + "............: ")

                if "Language_String" in audio_track:
                    write_info_list.append(encode_tracks[audio_track_index]["Language_String"])
                elif "Language" in audio_track:
                    write_info_list.append(encode_tracks[audio_track_index]["Language"])
                else:
                    logger.warning("音轨" + str(audio_track_id) + "缺少语言信息，请自行填写")
                    write_info_list.append("Ambiguous!!!")

                write_info_list.append(", " + encode_tracks[audio_track_index]
                ["Channels"] + " channels, " + encode_tracks[audio_track_index]["Format"])
                audio_track_id += 1
    except Exception as e:
        logger.warning(e)
        logger.warning("异常的音轨")
    # 写字幕轨参数
    subtitle_track_id = 1
    try:
        for subtitle_track_index, subtitle_track in enumerate(encode_tracks):
            if subtitle_track["@type"] == "Text":
                write_info_list.append("\n" + "SUBTITLE#" + str(subtitle_track_id).zfill(2) + ".........: ")

                if "Language_String" in subtitle_track and "Title" not in subtitle_track:
                    write_info_list.append(
                        encode_tracks[subtitle_track_index]["Language_String"])
                elif "Language" in subtitle_track and "Title" not in subtitle_track:
                    write_info_list.append(
                        encode_tracks[subtitle_track_index]["Language"])
                elif "Title" in subtitle_track:
                    write_info_list.append(
                        encode_tracks[subtitle_track_index]["Title"])
                else:
                    logger.warning("字幕轨" + str(subtitle_track_id) + "缺少语言信息，请自行填写")
                    write_info_list.append("Ambiguous!!!")

                write_info_list.append(
                    ", " + encode_tracks[subtitle_track_index]["Format"])
                subtitle_track_id += 1
    except Exception as e:
        logger.warning(e)
        logger.warning("异常的字幕轨")

    write_info_list.append("\n" + "SOURCE..............: " + encode_or_dl)
    write_info_list.append("\n" + "UPLOADER............: " + uploader_name + "\n")

    logger.info("Mediainfo-mini生成成功")
    return write_info_list
