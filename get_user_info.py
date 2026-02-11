#!/usr/bin/env python3
"""
飞书用户信息查询工具
"""

import requests
import json
from datetime import datetime

def load_token():
    """加载访问令牌"""
    try:
        with open('token.json', 'r') as f:
            token_data = json.load(f)
        return token_data['access_token']
    except Exception as e:
        print(f"❌ 无法加载token: {e}")
        return None

def get_user_info():
    """获取当前用户信息"""
    token = load_token()
    if not token:
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    # 尝试不同的用户API端点
    endpoints = [
        "https://open.feishu.cn/open-apis/contact/v3/users/me",
        "https://open.feishu.cn/open-apis/authen/v1/user_info"
    ]
    
    print("🔍 正在查询用户信息...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            print(f"尝试端点: {endpoint}")
            response = requests.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 成功获取用户信息:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return data
            else:
                print(f"⚠️  状态码: {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    print("\n💡 提示: 当前令牌权限可能不足以获取详细用户信息")
    print("   权限范围: auth:user.id:read (仅能读取用户ID)")

def decode_jwt_payload():
    """解码JWT载荷信息"""
    token = load_token()
    if not token:
        return
    
    try:
        # 分离JWT各部分
        header, payload, signature = token.split('.')
        
        # 解码payload (需要补全base64编码)
        import base64
        missing_padding = len(payload) % 4
        if missing_padding:
            payload += '=' * (4 - missing_padding)
        
        decoded_payload = base64.urlsafe_b64decode(payload)
        payload_json = json.loads(decoded_payload)
        
        print("\n🔐 JWT载荷信息:")
        print("=" * 30)
        for key, value in payload_json.items():
            if key in ['iat', 'exp', 'auth_time', 'auth_exp']:
                # 转换时间戳为可读格式
                try:
                    dt = datetime.fromtimestamp(value)
                    print(f"{key}: {value} ({dt.strftime('%Y-%m-%d %H:%M:%S')})")
                except:
                    print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")
                
    except Exception as e:
        print(f"❌ 解码JWT失败: {e}")

if __name__ == "__main__":
    print("👥 飞书用户信息查询工具")
    print("=" * 30)
    
    # 显示JWT信息
    decode_jwt_payload()
    
    # 尝试获取用户详情
    get_user_info()