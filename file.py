import os
import shutil
import subprocess
import requests
import threading
from concurrent.futures import ThreadPoolExecutor
def get_project():
    """获取指定路径下的所有项目名"""
    path="project"
    folders = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                folders.append(entry.name)
    return folders

def project_rename(old_name,new_name):
    """用于对项目进行重命名"""
    os.rename(old_name, new_name)

def new_project(name,dr):
    """用于创建一个新的项目
       参数说明:
       name:项目的名称
       dr:是否加载默认资源
       """
    os.makedirs("project", exist_ok=True) # 创建project文件夹，防止因为找不到路径而报错。不过疑似可以删掉这一行。
    shutil.copytree(".\VNE\VNE-0.1.0", f"project\{name}")
    print("项目基本结构创建完成")
    if dr:
        shutil.copytree("defrult_resources\\blueprint", f"project\{name}\\application\\blueprint")
        shutil.copytree("defrult_resources\\resources", f"project\{name}\\application\\resources")
        print("已成功加载默认资源")
    else:
        print("未加载默认资源")
        os.makedirs(f"project\{name}\\application\\resources", exist_ok=True)
        os.makedirs(f"project\{name}\\application\\blueprint", exist_ok=True)

def start_engineer(project_name):
    """用于启动编辑器"""
    subprocess.run(([f"project\{project_name}\RaycastEngine.exe"]),cwd=(f"project\{project_name}"))

def download(url, save_dir, num_threads, filename):
    """
    多线程下载文件（带进度显示）
    :param url: 下载链接
    :param save_dir: 保存目录
    :param num_threads: 线程数量
    :param filename: 保存的文件名
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    # 获取文件大小（通过 HEAD 请求）
    resp = requests.head(url, allow_redirects=True)
    resp.raise_for_status()
    file_size = int(resp.headers.get('content-length', 0))
    if file_size == 0:
        raise ValueError("无法获取文件大小，可能服务器不支持 Range")

    # 计算每个线程的下载区间
    part_size = file_size // num_threads
    ranges = [(i * part_size, (i + 1) * part_size - 1 if i < num_threads - 1 else file_size - 1) for i in range(num_threads)]

    # 临时文件列表
    part_files = [f"{file_path}.part{i}" for i in range(num_threads)]

    # 进度相关变量
    downloaded = [0] * num_threads
    lock = threading.Lock()
    
    def download_part(start, end, part_file, thread_id):
        headers = {'Range': f'bytes={start}-{end}'}
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(part_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        with lock:
                            downloaded[thread_id] += len(chunk)

    # 启动线程池下载
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(download_part, start, end, part_file, i)
                   for i, ((start, end), part_file) in enumerate(zip(ranges, part_files))]
        
        # 进度显示线程
        def show_progress():
            total = 0
            while total < file_size:
                total = sum(downloaded)
                percent = (total / file_size) * 100
                print(f"\r下载进度: {percent:.2f}% ({total}/{file_size} bytes)", end='', flush=True)
                import time
                time.sleep(0.5)
        
        progress_thread = threading.Thread(target=show_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        # 等待所有下载线程完成
        for future in futures:
            future.result()
        
        # 下载完成，打印最终进度
        print(f"\r下载进度: 100.00% ({file_size}/{file_size} bytes)")

    # 合并分块文件
    with open(file_path, 'wb') as outfile:
        for part_file in part_files:
            with open(part_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(part_file)  # 删除临时文件
    
    print(f"文件已保存到: {file_path}")