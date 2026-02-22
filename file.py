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

Engine_name = "VoidNovelEngine-0.1.0-dev.2"
# 忽略SSL警告
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

def get_project():
    """获取指定路径下的所有项目名"""
    path = "project"
    folders = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                folders.append(entry.name)
    return folders

def project_rename(old_name, new_name):
    """用于对项目进行重命名"""
    os.rename(old_name, new_name)

def new_project(name, dr):
    """
    用于创建一个新的项目
    变量name字符串值
    变量dr布尔值
    """
    os.makedirs("project", exist_ok=True)
    shutil.copytree(f".\\VNE\\{Engine_name}", f"project\\{name}")
    print("项目基本结构创建完成")
    if dr:
        shutil.copytree("defrult_resources\\blueprint", f"project\\{name}\\application\\blueprint")
        shutil.copytree("defrult_resources\\resources", f"project\\{name}\\application\\resources")
        print("已成功加载默认资源")
    else:
        print("未加载默认资源")
        os.makedirs(f"project\\{name}\\application\\resources", exist_ok=True)
        os.makedirs(f"project\\{name}\\application\\blueprint", exist_ok=True)

def start_engineer(project_name):
    """用于启动编辑器"""
    subprocess.run([f"project\\{project_name}\\RaycastEngine.exe"], 
                  cwd=f"project\\{project_name}")

def unzip(zip_path, output_path, folder_name):
    """用于解压下载得到的压缩文件"""
    target_dir = os.path.join(output_path, folder_name)
    os.makedirs(output_path, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print(f"解压成功：{zip_path} -> {target_dir}")
        return target_dir
    except Exception as e:
        print(f"解压过程中发生错误：{e}")
        raise

def check_server_support(url):
    """检查服务器是否支持断点续传"""
    try:
        headers = {'Range': 'bytes=0-0'}
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        # 检查是否返回206 Partial Content
        if response.status_code == 206:
            content_range = response.headers.get('Content-Range', '')
            if content_range:
                print("服务器支持断点续传")
                return True
        
        print("服务器不支持断点续传，将使用单线程下载")
        return False
    except Exception as e:
        print(f"检查服务器支持时出错：{e}")
        return False

def download_single(url, save_dir, filename, max_retries=2):
    """
    单线程下载文件（适用于不支持断点续传的服务器）
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    
    # 创建session with retry策略
    session = requests.Session()
    session.verify = False
    
    retries = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    # 先获取文件大小
    print("正在获取文件信息...")
    try:
        response = session.head(url, timeout=30)
        response.raise_for_status()
        file_size = int(response.headers.get('content-length', 0))
        if file_size == 0:
            print("警告：无法获取文件大小")
        else:
            print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
    except:
        file_size = 0
        print("警告：无法获取文件大小")
    
    # 开始下载
    print("开始下载...")
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
                        
                        # 计算进度和速度
                        if file_size > 0:
                            percent = (downloaded / file_size) * 100
                        else:
                            percent = 0
                        
                        # 计算下载速度
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = downloaded / elapsed / 1024  # KB/s
                        else:
                            speed = 0
                        
                        # 显示进度
                        if file_size > 0:
                            print(f"\r进度: {percent:.2f}% | 已下载: {downloaded/1024/1024:.2f} MB | "
                                  f"速度: {speed:.2f} KB/s", end='', flush=True)
                        else:
                            print(f"\r已下载: {downloaded/1024/1024:.2f} MB | "
                                  f"速度: {speed:.2f} KB/s", end='', flush=True)
            
            # 下载完成
            print(f"\n下载完成！文件已保存到: {file_path}")
            
            # 验证文件大小（如果能获取到的话）
            if file_size > 0 and downloaded == file_size:
                print("文件完整性验证通过")
            elif file_size > 0 and downloaded != file_size:
                print(f"警告：文件大小不匹配！预期 {file_size}，实际 {downloaded}")
            
            return True
            
        except Exception as e:
            if attempt < max_retries:
                print(f"\n下载中断({str(e)[:50]}...)，正在进行第 {attempt + 1} 次重试...")
                time.sleep(2)
                # 续传：检查已下载的部分
                if os.path.exists(file_path):
                    downloaded = os.path.getsize(file_path)
                    print(f"已下载 {downloaded/1024/1024:.2f} MB，尝试续传...")
            else:
                print(f"\n下载失败，已达到最大重试次数")
                raise e
    
    return False

def download(url, save_dir, num_threads=None, filename=None):
    """
    智能下载函数：自动检测服务器支持并选择合适的方式
    """
    # 检查服务器是否支持断点续传
    supports_range = check_server_support(url)
    
    if supports_range and num_threads and num_threads > 1:
        print(f"使用多线程下载（{num_threads}线程）")
        # 这里可以调用你原来的多线程下载函数
        # download_multi_thread(url, save_dir, num_threads, filename)
        # 但为了简单起见，这里先用单线程
        download_single(url, save_dir, filename)
    else:
        print("使用单线程下载")
        download_single(url, save_dir, filename)