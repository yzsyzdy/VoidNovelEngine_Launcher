import os
import time
import shutil
import main
import file
import gui
from main import gui_print

print("=" * 50)
print("\n欢迎使用VoidNovelEngine_Launcher\n")
print("=" * 50)

if not os.path.exists("VNE"):
    user_input = input("未检测到VNE引擎，是否自动安装(Y/N)：")
    url = "https://gitee.com/yzsyzdy/VoidNovelEngine/releases/download/0.1.0.dev.2/VoidNovelEngine-0.1.0-dev.2.zip"
    if user_input.lower() == "y":
        print("开始调用国内镜像下载")
        file.download(url=url, save_dir=".", num_threads=8, filename="VNE.zip")
        os.makedirs("VNE", exist_ok=True)
        print("开始解压下载文件")
        file.unzip(zip_path="VNE.zip", output_path=".", folder_name="VNE")
        # 删除不必要的目录
        os.remove('VNE.zip')
    else:
        print("未下载VNE引擎，程序无法启动")
        exit()

time.sleep(1)
# 启动 PyQt5 GUI
gui.run_gui()