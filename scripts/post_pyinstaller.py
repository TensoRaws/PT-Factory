import shutil
from pathlib import Path

projectPATH = Path(__file__).resolve().parent.parent.absolute()


def post_pyinstaller() -> None:
    print("-" * 50)
    shutil.copy(projectPATH / "config.yaml", projectPATH / "dist/ptf/config.yaml")
    print("Copied config to dist folder~")
    print("-" * 50)


if __name__ == "__main__":
    post_pyinstaller()
