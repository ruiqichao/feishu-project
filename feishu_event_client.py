#!/usr/bin/env python3
"""
飞书长连接事件客户端
使用官方SDK启动长连接客户端并处理事件回调
"""

import json
import threading
import time
from larksuiteoapi import Config, APP_TYPE_INTERNAL, DOMAIN_FEISHU, DefaultLogger, LEVEL_INFO, MemoryStore
from larksuiteoapi.event import set_event_callback, handle_event
from larksuiteoapi.service.im.v1 import MessageReceiveEvent
import larksuiteoapi
from flask import Flask, request, jsonify
import os

# 飞书应用配置
APP_ID = "cli_a9004b0c0ef8dcc0"
APP_SECRET = "klGdfo4W52Q9Hd6OZkBtbs3cv0ZFsJvT"
APP_TYPE = APP_TYPE_INTERNAL  # 内部应用

class FeishuEventClient:
    def __init__(self):
        """初始化飞书事件客户端"""
        # 创建配置对象
        app_settings = Config.new_internal_app_settings(
            app_id=APP_ID,
            app_secret=APP_SECRET
        )
        self.config = Config.new_config(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_INFO, MemoryStore())
        
        # 连接状态
        self.is_connected = False
        self.flask_app = Flask(__name__)
        self.setup_routes()
        
    def message_callback(self, ctx, event: MessageReceiveEvent):
        """消息接收回调函数"""
        print(f"📥 收到消息事件:")
        print(f"   消息ID: {event.message.message_id}")
        print(f"   发送者: {event.sender.sender_id.user_id}")
        print(f"   消息类型: {event.message.message_type}")
        print(f"   内容: {event.message.content}")
        
        # 可以在这里添加消息处理逻辑
        # 例如：自动回复、消息转发等
        
    def setup_event_handlers(self):
        """设置事件处理器"""
        # 注册消息接收事件回调
        set_event_callback(
            self.config, 
            "im.message.receive_v1", 
            self.message_callback
        )
        
    def setup_routes(self):
        """设置Flask路由"""
        @self.flask_app.route('/webhook/event', methods=['POST'])
        def event_handler():
            try:
                # 构建请求对象
                req = {
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers),
                    'body': request.get_data(as_text=True)
                }
                
                # 处理事件
                handle_event(self.config, req)
                
                # 如果是挑战请求，返回challenge
                body = request.get_json()
                if body and 'challenge' in body:
                    return jsonify({'challenge': body['challenge']}), 200
                
                return jsonify({'success': True}), 200
            except Exception as e:
                print(f"❌ 处理事件失败: {e}")
                return jsonify({'error': str(e)}), 500
    
    def start_event_listener(self):
        """启动事件监听器"""
        print("🚀 启动飞书长连接事件客户端...")
        
        try:
            # 设置事件处理器
            self.setup_event_handlers()
            
            print("📡 开始监听飞书事件...")
            self.is_connected = True
            
            print("✅ 飞书长连接客户端启动成功!")
            print("💡 客户端已就绪，等待事件触发...")
            print("🌐 监听地址: http://localhost:8080/webhook/event")
            
            # 启动Flask服务器
            self.flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
                
        except Exception as e:
            print(f"❌ 启动事件监听器失败: {e}")
            self.is_connected = False
            
    def stop_event_listener(self):
        """停止事件监听器"""
        print("🛑 正在停止飞书事件客户端...")
        self.is_connected = False
        print("✅ 飞书事件客户端已停止")

def main():
    """主函数"""
    print("🤖 飞书长连接事件客户端")
    print("=" * 40)
    
    # 创建客户端实例
    client = FeishuEventClient()
    
    try:
        # 启动事件监听
        client.start_event_listener()
        
    except KeyboardInterrupt:
        print("\n⚠️  收到中断信号")
        client.stop_event_listener()
        
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        client.stop_event_listener()

if __name__ == "__main__":
    main()