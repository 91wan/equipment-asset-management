#!/usr/bin/env python3
"""
Equipment Asset Management - GitHub Sync
同步设备数据到 GitHub Gist 或 Repository
"""

import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


class GitHubSync:
    """GitHub 同步器"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """发送 GitHub API 请求"""
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(url, method=method)
        
        for key, value in self.headers.items():
            req.add_header(key, value)
        
        if data:
            req.add_header("Content-Type", "application/json")
            json_data = json.dumps(data).encode('utf-8')
            req.data = json_data
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ API 错误: {e.code}")
            print(f"   {error_body}")
            raise
    
    def get_user(self) -> dict:
        """获取当前用户信息"""
        try:
            return self._request("GET", "/user")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("❌ Token 权限不足，无法获取用户信息")
                print("   建议添加 'read:user' scope")
            raise
    
    def create_gist(self, filename: str, content: str, description: str = "", public: bool = False) -> dict:
        """创建 GitHub Gist"""
        data = {
            "public": public,
            "description": description or f"Equipment Asset Management - {datetime.now().strftime('%Y-%m-%d')}",
            "files": {
                filename: {
                    "content": content
                }
            }
        }
        return self._request("POST", "/gists", data)
    
    def update_gist(self, gist_id: str, filename: str, content: str) -> dict:
        """更新现有 Gist"""
        data = {
            "files": {
                filename: {
                    "content": content
                }
            }
        }
        return self._request("PATCH", f"/gists/{gist_id}", data)
    
    def get_gist(self, gist_id: str) -> dict:
        """获取 Gist 信息"""
        return self._request("GET", f"/gists/{gist_id}")
    
    def list_gists(self, per_page: int = 10) -> list:
        """列出用户的 Gists"""
        return self._request("GET", f"/gists?per_page={per_page}")
    
    def sync_to_repo(self, owner: str, repo: str, path: str, content: str, message: str = None) -> dict:
        """同步到指定仓库的文件"""
        # 获取文件 SHA（如果存在）
        try:
            file_info = self._request("GET", f"/repos/{owner}/{repo}/contents/{path}")
            sha = file_info.get("sha")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                sha = None
            else:
                raise
        
        # 创建/更新文件
        data = {
            "message": message or f"Update equipment data - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
        }
        if sha:
            data["sha"] = sha
        
        return self._request("PUT", f"/repos/{owner}/{repo}/contents/{path}", data)


def format_as_markdown(data: dict) -> str:
    """将数据格式化为 Markdown"""
    meta = data.get("meta", {})
    equipment = data.get("equipment", [])
    
    lines = [
        "# 🖥️ Equipment Asset Registry",
        "",
        f"> Last updated: {meta.get('calculated_at', datetime.now().strftime('%Y-%m-%d'))}",
        f"> Base currency: {meta.get('base_currency', 'CNY')}",
        "",
        "## 📊 Summary",
        "",
        f"- **Total Equipment**: {meta.get('total_equipment', len(equipment))} items",
        f"- **Total Investment**: {meta.get('total_price', 0):,.0f}",
        f"- **Residual Value**: {meta.get('total_residual', 0):,.0f}",
        "",
        "## 📋 Equipment List",
        "",
        "| Name | Category | Purchase Date | Price | Days Used | Daily Cost | Status | Residual |",
        "|:---|:---|:---|---:|---:|---:|:---|---:|",
    ]
    
    for item in equipment:
        lines.append(
            f"| {item.get('name', 'N/A')} | "
            f"{item.get('category', 'other')} | "
            f"{item.get('purchase_date', '-')} | "
            f"{item.get('price', 0):,.0f} | "
            f"{item.get('days_used', 0)} | "
            f"{item.get('daily_cost', 0):.2f} | "
            f"{item.get('status_emoji', '⚪')} {item.get('status', 'unknown')} | "
            f"{item.get('residual_value', 0):,.0f} |"
        )
    
    lines.extend([
        "",
        "---",
        "",
        "_Generated by Equipment Asset Management_",
        ""
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="同步设备数据到 GitHub")
    parser.add_argument("--registry", "-r", required=True, help="设备数据 JSON 文件路径")
    parser.add_argument("--token", "-t", help="GitHub Token（也可从 GITHUB_TOKEN 环境变量获取）")
    parser.add_argument("--mode", "-m", choices=["gist", "repo"], default="gist", help="同步模式")
    
    # Gist 模式参数
    parser.add_argument("--gist-id", "-g", help="现有 Gist ID（更新模式）")
    parser.add_argument("--gist-public", action="store_true", help="创建公开 Gist")
    
    # Repo 模式参数
    parser.add_argument("--repo-owner", "-o", help="仓库所有者")
    parser.add_argument("--repo-name", "-n", help="仓库名称")
    parser.add_argument("--file-path", "-p", default="equipment-data.md", help="仓库内文件路径")
    
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown", help="输出格式")
    args = parser.parse_args()
    
    # 获取 Token
    token = args.token or __import__('os').environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ 错误: 请提供 GitHub Token")
        print("   方法1: --token 参数")
        print("   方法2: GITHUB_TOKEN 环境变量")
        return 1
    
    # 加载数据
    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"❌ 文件不存在: {registry_path}")
        return 1
    
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 初始化同步器
    sync = GitHubSync(token)
    
    # 验证 Token
    print("🔐 验证 GitHub Token...")
    try:
        user = sync.get_user()
        print(f"   ✅ 登录成功: @{user.get('login', 'unknown')}")
    except Exception as e:
        print(f"   ⚠️  无法获取用户信息（Token 可能缺少 scope）")
    
    # 根据格式准备内容
    if args.format == "markdown":
        content = format_as_markdown(data)
        filename = "equipment-registry.md"
    else:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        filename = "equipment-data.json"
    
    # 同步
    if args.mode == "gist":
        print("\n📤 同步到 GitHub Gist...")
        
        if args.gist_id:
            # 更新现有 Gist
            try:
                result = sync.update_gist(args.gist_id, filename, content)
                print(f"   ✅ Gist 更新成功!")
                print(f"   🌐 URL: {result['html_url']}")
            except Exception