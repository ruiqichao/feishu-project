"""
飞书 OAuth2 获取 user_access_token

流程：
1. 启动本地 HTTP 服务器监听回调
2. 打开浏览器让用户在飞书授权页面登录授权
3. 接收授权码(code)
4. 用授权码换取 user_access_token
"""

import http.server
import json
import secrets
import threading
import urllib.parse
import webbrowser
import os

import requests

# ===== 配置 =====
CLIENT_ID = "cli_a9004b0c0ef8dcc0"
CLIENT_SECRET = "klGdfo4W52Q9Hd6OZkBtbs3cv0ZFsJvT"
REDIRECT_URI = "http://localhost:9000/callback"
LOCAL_PORT = 9000

# 飞书 API 地址
AUTHORIZE_URL = "https://accounts.feishu.cn/open-apis/authen/v1/authorize"
TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v2/oauth/token"
REFRESH_TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v2/oauth/token"

def build_authorize_url(state: str) -> str:
    """构建飞书授权链接"""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": state,
        "scope": "auth:user.id:read",
    }
    return f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code: str) -> dict:
    """用授权码换取 user_access_token"""
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    resp = requests.post(
        TOKEN_URL,
        json=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(refresh_token: str) -> dict:
    """使用刷新令牌获取新的 user_access_token"""
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    resp = requests.post(
        REFRESH_TOKEN_URL,
        json=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    resp.raise_for_status()
    return resp.json()


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    """处理飞书 OAuth 回调"""

    auth_code = None
    received_state = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        qs = urllib.parse.parse_qs(parsed.query)
        CallbackHandler.auth_code = qs.get("code", [None])[0]
        CallbackHandler.received_state = qs.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("授权成功！你可以关闭此页面。".encode("utf-8"))

        # 在后台线程中关闭服务器
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, format, *args):
        pass  # 静默日志


def main():
    state = secrets.token_urlsafe(16)
    auth_url = build_authorize_url(state)

    print("=" * 60)
    print("飞书 OAuth2 - 获取 user_access_token")
    print("=" * 60)
    print(f"\n请在浏览器中打开以下链接完成授权：\n\n{auth_url}\n")

    # 尝试自动打开浏览器
    try:
        webbrowser.open(auth_url)
        print("（已尝试自动打开浏览器）")
    except Exception:
        print("（无法自动打开浏览器，请手动复制上方链接）")

    print(f"\n等待回调中... (监听 http://localhost:{LOCAL_PORT}/callback)\n")

    server = http.server.HTTPServer(("localhost", LOCAL_PORT), CallbackHandler)
    server.serve_forever()

    # 验证 state
    if CallbackHandler.received_state != state:
        print("[错误] state 不匹配，可能存在 CSRF 攻击风险")
        return

    code = CallbackHandler.auth_code
    if not code:
        print("[错误] 未收到授权码")
        return

    print(f"收到授权码: {code[:20]}...")
    print("\n正在换取 user_access_token ...\n")

    result = exchange_code_for_token(code)

    if result.get("code") != 0:
        print(f"[错误] 获取 token 失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return

    data = result.get("data", result)
    print("获取 user_access_token 成功！")
    print("-" * 60)
    print(f"  access_token:  {data.get('access_token', 'N/A')}")
    print(f"  token_type:    {data.get('token_type', 'N/A')}")
    print(f"  expires_in:    {data.get('expires_in', 'N/A')} 秒")
    print(f"  refresh_token: {data.get('refresh_token', 'N/A')}")
    print(f"  open_id:       {data.get('open_id', 'N/A')}")
    print(f"  name:          {data.get('name', 'N/A')}")
    print("-" * 60)

    # 保存到文件
    with open("token.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\ntoken 已保存到 token.json")


def refresh_token_main():
    """刷新令牌的主函数"""
    try:
        # 读取现有的token.json文件
        with open("token.json", "r", encoding="utf-8") as f:
            token_data = json.load(f)
        
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            print("错误：token.json中没有找到refresh_token")
            return
        
        print("正在刷新 user_access_token...")
        result = refresh_access_token(refresh_token)
        
        if result.get("code") != 0:
            print(f"[错误] 刷新 token 失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return
        
        data = result.get("data", result)
        print("刷新 user_access_token 成功！")
        print("-" * 60)
        print(f"  access_token:  {data.get('access_token', 'N/A')}")
        print(f"  token_type:    {data.get('token_type', 'N/A')}")
        print(f"  expires_in:    {data.get('expires_in', 'N/A')} 秒")
        print(f"  refresh_token: {data.get('refresh_token', 'N/A')}")
        print(f"  scope:         {data.get('scope', 'N/A')}")
        print("-" * 60)
        
        # 更新token.json文件
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\ntoken.json 已更新")
        
    except FileNotFoundError:
        print("错误：未找到 token.json 文件，请先运行获取令牌流程")
    except Exception as e:
        print(f"刷新令牌时发生错误: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "refresh":
        refresh_token_main()
    else:
        main()