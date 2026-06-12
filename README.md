# AgentLens

小米 Watch S5 AI Agent 审批工具 - 通过手表远程审批 Claude Code 危险操作，并在任务完成时自动收到通知。

> "AI 在干活,你在摸鱼;危险操作抬腕一点,任务跑完手表喊你。"

## 功能特性

- 🚨 **远程审批** — `rm -rf`、`git push --force` 等危险命令推送到手表，支持允许/拒绝按钮
- ✅ **选择题推送** — Claude 的多选决策框也可在手表上直接作答
- 🔔 **完成提醒** — 任务结束后手表震动通知
- ⚠️ **限额预警** — 订阅额度耗尽时即时通知
- 📱 **多窗口并行** — 各窗口独立审批通道，通知标注项目名

## 技术架构

| 组件 | 技术方案 |
|------|---------|
| 手表端 | Vela 5.0 小程序 |
| PC 端 | Python 脚本 |
| 通信层 | ntfy.sh |
| 集成 | Claude Code Hooks |

## 前置条件

- 小米 Watch S5（480×480 圆形屏幕）
- AIoT IDE
- Node.js 环境
- Python 3
- ntfy.sh 账号（免费）
- Claude Code CLI

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置 ntfy.sh

1. 访问 [ntfy.sh](https://ntfy.sh)
2. 创建一个 topic（无需注册）
3. 复制 `watch.env.example` 为 `watch.env`
4. 填入你的 topic 名称

```bash
cp watch.env.example watch.env
# 编辑 watch.env 文件
```

### 3. 配置 Claude Code

将以下内容添加到 Claude Code 的 settings.json 中：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python watch_approve.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python watch_done.py"
          }
        ]
      }
    ]
  }
}
```

### 4. 启动手表应用

```bash
npm start
```

### 5. 在手表上配置

1. 打开手表上的 "Watch Approve" 应用
2. 进入设置页面
3. 输入你的 ntfy topic
4. 测试连接

## 项目结构

```
AgentLens/
├── README.md                    # 项目说明
├── DEVELOPMENT_PLAN.md          # 开发计划
├── watch.env.example            # 环境变量配置模板
├── watch_approve.py             # 审批 hook 主脚本
├── watch_done.py                # 任务完成通知脚本
├── create-s5-emulator.js        # 模拟器创建脚本
├── package.json                 # Vela 项目配置
├── src/
│   ├── manifest.json            # Vela 应用配置
│   ├── app.ux                   # 应用入口
│   ├── pages/
│   │   ├── approve/             # 审批页面
│   │   ├── notify/              # 通知页面
│   │   └── settings/            # 设置页面
│   ├── common/
│   │   ├── api.js               # 网络请求封装
│   │   ├── config.js            # 配置管理
│   │   ├── utils.js             # 工具函数
│   │   └── logo.png             # 应用图标
│   └── style/
│       └── comm.css             # 公共样式
└── examples/
    └── claude-code-settings.json
```

## 工作原理

1. 当 Claude Code 执行危险命令时，`watch_approve.py` 被调用
2. 脚本通过 ntfy.sh 发送审批请求到手表
3. 手表端显示审批界面，用户点击允许/拒绝
4. 审批结果通过 ntfy.sh 返回给脚本
5. 脚本将结果返回给 Claude Code

## 安全特性

- **Fail-safe 设计**：网络故障或超时时自动退回终端审批
- **危险命令检测**：内置常见危险命令正则匹配
- **保护路径**：防止 agent 修改关键文件
- **超时自动拒绝**：默认 60 秒超时

## 参考资源

- [agent-watch-approve 原项目](https://github.com/ghy196830-del/agent-watch-approve)
- [小米 Vela 开发文档](https://iot.mi.com/vela)
- [ntfy.sh 官网](https://ntfy.sh)
- [Claude Code Hooks 文档](https://docs.anthropic.com/claude-code)

## 许可证

MIT License
