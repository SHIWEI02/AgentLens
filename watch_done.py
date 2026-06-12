#!/usr/bin/env python3
"""
小米 Watch S5 AI Agent 审批工具 - 任务完成通知脚本

当 Claude Code 任务完成时，此脚本会被调用，
通过 ntfy.sh 向手表发送完成通知。

用法：
  python watch_done.py

环境变量：
  NTFY_TOPIC - ntfy.sh 的 topic 名称
  NTFY_SERVER - ntfy.sh 服务器地址（默认 https://ntfy.sh）
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

# 加载环境变量
def load_env():
    """从 watch.env 文件加载环境变量"""
    env_file = os.path.join(os.path.dirname(__file__), 'watch.env')
    env_vars = {}

    # 默认值
    env_vars['NTFY_SERVER'] = 'https://ntfy.sh'

    # 从文件读取
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip()

    # 环境变量覆盖
    for key in env_vars:
        env_vars[key] = os.environ.get(key, env_vars[key])

    return env_vars

# 发送完成通知
def send_completion_notification(topic, server, status="success", message=""):
    """通过 ntfy.sh 发送完成通知"""
    try:
        # 根据状态选择图标和标签
        if status == "success":
            title = "✅ 任务完成"
            tags = ["white_check_mark", "success"]
            icon = "🎉"
        elif status == "error":
            title = "❌ 任务失败"
            tags = ["x", "error"]
            icon = "😞"
        else:
            title = "ℹ️ 任务状态"
            tags = ["information_source"]
            icon = "📌"

        # 构建消息
        full_message = f"{icon} {message}" if message else title

        # 发送到 ntfy.sh
        url = f"{server}/{topic}"
        data = json.dumps({
            "topic": topic,
            "title": title,
            "message": full_message,
            "tags": tags,
            "priority": "default"
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True
    except Exception as e:
        print(f"发送完成通知失败: {e}", file=sys.stderr)

    return False

def main():
    """主函数"""
    # 从 stdin 读取 Claude Code 传入的数据
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    # 获取任务状态
    status = input_data.get('status', 'success')
    message = input_data.get('message', '')

    # 加载配置
    env = load_env()

    topic = env.get('NTFY_TOPIC')
    if not topic:
        print("错误: 未配置 NTFY_TOPIC", file=sys.stderr)
        sys.exit(1)

    server = env['NTFY_SERVER']

    # 发送完成通知
    if send_completion_notification(topic, server, status, message):
        print("✅ 完成通知已发送到手表", file=sys.stderr)
    else:
        print("❌ 发送完成通知失败", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
