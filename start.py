import main
import os
import file
import time
import shutil
os.system('cls')
print("="*50,"\n欢迎使用VNEHub\n","="*50,sep="")
if not os.path.exists("VNE"):
    user_input = input("未检测到VNE引擎，是否自动安装(Y/N)")
    url="https://gitee.com/yzsyzdy/VoidNovelEngine/releases/download/0.1.0.dev.2/VoidNovelEngine-0.1.0-dev.2.zip"
    if user_input == "Y" or user_input == "y":
        print("开始调用国内镜像下载")
        file.download(url=url,save_dir=".\\",num_threads=8,filename="VNE.zip")
        os.makedirs("VNE", exist_ok=True)
        print("开始解压下载文件")
        file.unzip(zip_path=".\VNE.zip",output_path=".\\",folder_name="VNE")
        shutil.rmtree("VNE\VoidNovelEngine-0.1.0-dev.2\\application\\blueprint")
        shutil.rmtree("VNE\VoidNovelEngine-0.1.0-dev.2\\application\\flow")
        shutil.rmtree("VNE\VoidNovelEngine-0.1.0-dev.2\\application\\resources")
    elif user_input == "N" or user_input == "n":
        print("未下载VNE引擎，程序无法启动")
        exit()
time.sleep(1)
main.menu()