import requests
import os
from typing import List, Dict, Optional
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_github_releases(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """
    获取GitHub仓库的所有release信息（跳过SSL验证）
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {"Accept": "application/vnd.github.v3+json"}

    if token is None:
        token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    releases = []
    page = 1
    per_page = 100

    with requests.Session() as session:
        session.headers.update(headers)
        
        while True:
            params = {"page": page, "per_page": per_page}
            try:
                # 添加 verify=False 跳过SSL验证
                response = session.get(url, params=params, verify=False)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    print(f"仓库 {owner}/{repo} 不存在")
                    return []
                else:
                    print(f"HTTP错误: {e}")
                    return []
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                return []

            data = response.json()
            if not data:
                break

            releases.extend(data)

            if "next" not in response.links:
                break
            page += 1

    return releases
# 获取 fastapi 项目的 release 列表
releases = get_github_releases("yzsyzdy", "mc_map")
for r in releases:
    print(f"{r['tag_name']}: {r['name']} - {r['published_at']}")