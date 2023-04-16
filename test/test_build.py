import pathlib
import os

projectPATH = pathlib.Path(os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

_encode_path = projectPATH / "assets" / "Kimetsu no Yaiba S04E01 2023 2160p B-Global WEB-DL x264 AAC-AnimeS@ADWeb.mp4"

_build = projectPATH / "dist" / "ptf"

_command = str(_build) + " -e " + "\"" + str(_encode_path) + "\""
print(_command)
os.system(_command)
