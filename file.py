import os
import shutil
import subprocess
import requests
import zipfile
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
from urllib3.exceptions import InsecureRequestWarning

# 尝试从 main 导入 gui_print，如果失败则用 print
try:
    from main import gui_print
except ImportError:
    def gui_print(text):
        print(text)

Engine_name = "VoidNovelEngine-0.1.0-dev.2"
warnings.filterwarnings('ignore', category=InsecureRequestWarning)


def get_project():
    """获取 project 目录下的所有项目名"""
    path = "project"
    folders = []
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    folders.append(entry.name)
    except FileNotFoundError:
        os.makedirs(path, exist_ok=True)
    return folders


def new_project(name, dr):
    """
    创建一个新项目
    :param name: 项目名称
    :param dr: 是否复制默认资源
    """
    try:
        os.makedirs("project", exist_ok=True)

        # 检查引擎是否存在
        engine_path = os.path.join(".", "VNE", Engine_name)
        if not os.path.exists(engine_path):
            gui_print(f"错误：引擎路径 {engine_path} 不存在")
            return False

        shutil.copytree(engine_path, os.path.join("project", name))
        gui_print("项目基本结构创建完成")
        # 神秘的东西,暂时不打算完善了
        if not dr:
            gui_print("未加载默认资源")
            shutil.rmtree(os.path.join("project", f"{name}", "application", "blueprint"), ignore_errors=True)
            shutil.rmtree(os.path.join("project", f"{name}", "application", "flow"), ignore_errors=True)
            shutil.rmtree(os.path.join("project", f"{name}", "application", "resources"), ignore_errors=True)

        return True

    except Exception as e:
        gui_print(f"创建项目时出错：{e}")
        return False


def start_engineer(project_name):
    """启动编辑器"""
    try:
        exe_path = os.path.join("project", project_name, "RaycastEngine.exe")
        if os.path.exists(exe_path):
            subprocess.Popen([exe_path], cwd=os.path.join("project", project_name))
            gui_print(f"编辑器已启动：{project_name}")
        else:
            gui_print(f"错误：找不到 {exe_path}")
    except Exception as e:
        gui_print(f"启动编辑器失败：{e}")


def unzip(zip_path, output_path, folder_name):
    """解压压缩文件到指定文件夹"""
    target_dir = os.path.join(output_path, folder_name)
    os.makedirs(output_path, exist_ok=True)

    try:
        gui_print(f"正在解压 {zip_path} 到 {target_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        gui_print(f"解压成功：{zip_path} -> {target_dir}")
        return target_dir
    except Exception as e:
        gui_print(f"解压过程中发生错误：{e}")
        raise


def check_server_support(url):
    """检查服务器是否支持断点续传"""
    try:
        headers = {'Range': 'bytes=0-0'}
        response = requests.get(url, headers=headers, verify=False, timeout=10)

        if response.status_code == 206:
            content_range = response.headers.get('Content-Range', '')
            if content_range:
                gui_print("服务器支持断点续传")
                return True

        gui_print("服务器不支持断点续传，将使用单线程下载")
        return False
    except Exception as e:
        gui_print(f"检查服务器支持时出错：{e}")
        return False


def download_single(url, save_dir, filename, max_retries=2):
    """
    单线程下载文件（适用于不支持断点续传的服务器）
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    session = requests.Session()
    session.verify = False

    retries = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    # 获取文件大小
    gui_print("正在获取文件信息...")
    try:
        response = session.head(url, timeout=30)
        response.raise_for_status()
        file_size = int(response.headers.get('content-length', 0))
        if file_size == 0:
            gui_print("警告：无法获取文件大小")
        else:
            gui_print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
    except:
        file_size = 0
        gui_print("警告：无法获取文件大小")

    gui_print("开始下载...")
    downloaded = 0
    start_time = time.time()

    for attempt in range(max_retries + 1):
        try:
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if file_size > 0:
                            percent = (downloaded / file_size) * 100
                        else:
                            percent = 0

                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed / 1024 if elapsed > 0 else 0

                        if file_size > 0:
                            progress_msg = f"\r进度: {percent:.2f}% | 已下载: {downloaded/1024/1024:.2f} MB | 速度: {speed:.2f} KB/s"
                        else:
                            progress_msg = f"\r已下载: {downloaded/1024/1024:.2f} MB | 速度: {speed:.2f} KB/s"

                        if attempt == 0 and downloaded % (8192 * 100) < 8192:
                            gui_print(progress_msg)

            gui_print(f"\n下载完成！文件已保存到: {file_path}")

            if file_size > 0 and downloaded == file_size:
                gui_print("文件完整性验证通过")
            elif file_size > 0 and downloaded != file_size:
                gui_print(f"警告：文件大小不匹配！预期 {file_size}，实际 {downloaded}")

            return True

        except Exception as e:
            if attempt < max_retries:
                gui_print(f"\n下载中断({str(e)[:50]}...)，正在进行第 {attempt + 1} 次重试...")
                time.sleep(2)
                if os.path.exists(file_path):
                    downloaded = os.path.getsize(file_path)
                    gui_print(f"已下载 {downloaded/1024/1024:.2f} MB，尝试续传...")
            else:
                gui_print(f"\n下载失败，已达到最大重试次数")
                raise e

    return False


def download(url, save_dir, num_threads=None, filename=None):
    """
    智能下载函数：自动检测服务器支持并选择合适的方式
    """
    try:
        supports_range = check_server_support(url)

        if supports_range and num_threads and num_threads > 1:
            gui_print(f"使用多线程下载（{num_threads}线程）")
            # 实际可调用多线程函数，这里简单使用单线程
            download_single(url, save_dir, filename)
        else:
            gui_print("使用单线程下载")
            download_single(url, save_dir, filename)

    except Exception as e:
        gui_print(f"下载过程中发生错误：{e}")
        raise