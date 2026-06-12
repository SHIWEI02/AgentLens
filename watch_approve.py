#!/usr/bin/env python3
"""
小米 Watch S5 AI Agent 审批工具 - 审批 Hook 主脚本

当 Claude Code 执行危险命令时，此脚本会被调用，
通过 ntfy.sh 将审批请求推送到手表端。

用法：
  python watch_approve.py

环境变量：
  NTFY_TOPIC - ntfy.sh 的 topic 名称
  NTFY_SERVER - ntfy.sh 服务器地址（默认 https://ntfy.sh）
  APPROVE_TIMEOUT - 审批超时时间（秒，默认 60）
  DANGEROUS_COMMANDS - 危险命令列表（逗号分隔）
  PROTECTED_PATHS - 保护路径列表（逗号分隔）
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.error
import threading

# 加载环境变量
def load_env():
    """从 watch.env 文件加载环境变量"""
    env_file = os.path.join(os.path.dirname(__file__), 'watch.env')
    env_vars = {}

    # 默认值
    env_vars['NTFY_SERVER'] = 'https://ntfy.sh'
    env_vars['APPROVE_TIMEOUT'] = '60'
    env_vars['DANGEROUS_COMMANDS'] = 'rm -rf,sudo,git push --force,docker rm,docker prune,terraform destroy,chmod 777'
    env_vars['PROTECTED_PATHS'] = '.claude/hooks/,watch_approve.py,watch_done.py,watch.env'

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

# 危险命令检测
def is_dangerous_command(command, dangerous_commands):
    """检查命令是否包含危险操作"""
    patterns = [cmd.strip() for cmd in dangerous_commands.split(',')]
    for pattern in patterns:
        if pattern in command:
            return True
    return False

# 保护路径检测
def check_protected_paths(command, protected_paths):
    """检查命令是否涉及保护路径"""
    paths = [p.strip() for p in protected_paths.split(',')]
    for path in paths:
        if path in command:
            return True, path
    return False, None

# 发送审批请求到手表
def send_approval_request(command, topic, server, timeout):
    """通过 ntfy.sh 发送审批请求"""
    try:
        # 构建消息
        message = {
            "command": command,
            "timestamp": int(time.time()),
            "timeout": timeout
        }

        # 发送到 ntfy.sh
        url = f"{server}/{topic}"
        data = json.dumps({
            "topic": topic,
            "title": "⚠️ 危险命令审批",
            "message": f"命令: {command[:100]}...",
            "tags": ["warning", "approve"],
            "priority": "urgent",
            "actions": [
                {"action": "approve", "label": "✅ 允许", "type": "button"},
                {"action": "reject", "label": "❌ 拒绝", "type": "button"}
            ]
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True
    except Exception as e:
        print(f"发送审批请求失败: {e}", file=sys.stderr)

    return False

# 等待审批结果
def wait_for_approval(topic, server, timeout):
    """等待手表端的审批结果"""
    start_time = time.time()
    last_id = None

    while time.time() - start_time < timeout:
        try:
            # 轮询 ntfy.sh 获取最新消息
            url = f"{server}/{topic}/json?poll=1&since={last_id or '1m'}"
            req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=5) as response:
                for line in response:
                    try:
                        msg = json.loads(line.decode('utf-8'))
                        if 'id' in msg:
                            last_id = msg['id']

                        # 检查是否有审批结果
                        if msg.get('event') == 'action':
                            action = msg.get('action', {})
                            if action.get('action') == 'approve':
                                return True
                            elif action.get('action') == 'reject':
                                return False
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"轮询审批结果失败: {e}", file=sys.stderr)

        time.sleep(2)

    # 超时自动拒绝
    return False

def main():
    """主函数"""
    # 从 stdin 读取 Claude Code 传入的数据
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print("错误: 无法解析输入数据", file=sys.stderr)
        sys.exit(1)

    # 获取要执行的命令
    command = input_data.get('command', '')
    if not command:
        print("错误: 未找到命令", file=sys.stderr)
        sys.exit(1)

    # 加载配置
    env = load_env()

    # 检查是否是危险命令
    if not is_dangerous_command(command, env['DANGEROUS_COMMANDS']):
        # 非危险命令，直接放行
        print(json.dumps({"decision": "approve"}))
        sys.exit(0)

    # 检查是否涉及保护路径
    is_protected, protected_path = check_protected_paths(command, env['PROTECTED_PATHS'])
    if is_protected:
        print(json.dumps({
            "decision": "reject",
            "reason": f"命令涉及保护路径: {protected_path}"
        }))
        sys.exit(0)

    # 发送审批请求到手表
    topic = env.get('NTFY_TOPIC')
    if not topic:
        print("错误: 未配置 NTFY_TOPIC", file=sys.stderr)
        # 降级到终端审批
        print(f"\n⚠️  检测到危险命令: {command}")
        response = input("是否允许执行? (y/n): ").strip().lower()
        if response == 'y':
            print(json.dumps({"decision": "approve"}))
        else:
            print(json.dumps({"decision": "reject", "reason": "用户拒绝"}))
        sys.exit(0)

    server = env['NTFY_SERVER']
    timeout = int(env['APPROVE_TIMEOUT'])

    print(f"\n⚠️  检测到危险命令，正在推送到手表审批...", file=sys.stderr)
    print(f"命令: {command}", file=sys.stderr)

    # 发送审批请求
    if send_approval_request(command, topic, server, timeout):
        print(f"✅ 已推送到手表，等待审批 (超时: {timeout}秒)...", file=sys.stderr)

        # 等待审批结果
        if wait_for_approval(topic, server, timeout):
            print("✅ 手表审批通过", file=sys.stderr)
            print(json.dumps({"decision": "approve"}))
        else:
            print("❌ 手表审批拒绝或超时", file=sys.stderr)
            print(json.dumps({
                "decision": "reject",
                "reason": "手表审批拒绝或超时"
            }))
    else:
        print("❌ 无法推送到手表，降级到终端审批", file=sys.stderr)
        print(f"\n⚠️  检测到危险命令: {command}")
        response = input("是否允许执行? (y/n): ").strip().lower()
        if response == 'y':
            print(json.dumps({"decision": "approve"}))
        else:
            print(json.dumps({"decision": "reject", "reason": "用户拒绝"}))

if __name__ == '__main__':
    main()
