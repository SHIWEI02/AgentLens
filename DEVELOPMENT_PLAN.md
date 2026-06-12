# AgentLens - 开发计划

## 项目概述

参考 [agent-watch-approve](https://github.com/ghy196830-del/agent-watch-approve)，开发一个通过小米 Watch S5 远程审批 AI 编程代理（Claude Code）危险操作的工具。

- **项目名称**: AgentLens
- **包名**: com.swei.watch.agentlens

核心理念："AI 在干活,你在摸鱼;危险操作抬腕一点,任务跑完手表喊你。"

---

## 设备参数

| 参数 | 值 |
|------|-----|
| 设备型号 | 小米 Watch S5 |
| 屏幕形状 | 圆形 |
| 屏幕尺寸 | 1.48 英寸 AMOLED |
| 分辨率 | 480 × 480 px |
| 像素密度 | 323 PPI |
| 操作系统 | Vela 5.0 |

---

## 技术方案对比

| 功能 | 原项目 (Apple Watch) | 小米 Watch S5 方案 |
|------|---------------------|-------------------|
| 通知推送 | Pushcut (iOS) | ntfy.sh / WebSocket |
| 手表交互 | Pushcut 动态按钮 | Vela 小程序 + 本地服务 |
| 通信协议 | ntfy.sh (HTTP) | ntfy.sh 或 WebSocket |
| 开发语言 | Python (脚本) | Python (脚本) + JS (Vela 小程序) |

---

## 核心功能

1. **远程审批** — `rm -rf`、`git push --force` 等危险命令推送到手表，支持允许/拒绝按钮
2. **选择题推送** — Claude 的多选决策框也可在手表上直接作答
3. **完成提醒** — 任务结束后手表震动通知
4. **限额预警** — 订阅额度耗尽时即时通知
5. **多窗口并行** — 各窗口独立审批通道，通知标注项目名

---

## 开发阶段

### 阶段 1：基础架构搭建 (1-2天)

- [x] 搭建 Vela 5.0 开发环境
- [x] 创建小米 Watch S5 模拟器（480×480 圆形）
- [x] 设计项目目录结构
- [x] 配置 manifest.json

### 阶段 2：手表端小程序开发 (3-5天)

- [x] 创建 Vela 小程序项目
- [x] 实现通知接收界面
- [x] 实现审批按钮（允许/拒绝）
- [x] 实现震动反馈
- [ ] 测试模拟器效果

### 阶段 3：PC 端 Hook 脚本开发 (2-3天)

- [x] 编写 `watch_approve.py`（审批主脚本）
- [x] 编写 `watch_done.py`（完成通知脚本）
- [x] 实现危险命令检测逻辑
- [x] 集成 ntfy.sh 消息通道

### 阶段 4：通信层实现 (2-3天)

- [ ] 实现 ntfy.sh 消息订阅/发布
- [ ] 实现手表端消息轮询或 WebSocket
- [ ] 处理超时和网络异常（Fail-safe）

### 阶段 5：Claude Code 集成 (1-2天)

- [ ] 配置 Claude Code Hook
- [ ] 编写配置文件模板
- [ ] 测试完整审批流程

### 阶段 6：测试与优化 (2-3天)

- [ ] 模拟器测试
- [ ] 真机测试（如有设备）
- [ ] 优化用户体验
- [ ] 编写文档

---

## 项目目录结构

```
AgentLens/
├── README.md                    # 项目说明
├── DEVELOPMENT_PLAN.md          # 开发计划（本文件）
├── watch.env.example            # 环境变量配置模板
├── watch_approve.py             # 审批 hook 主脚本
├── watch_done.py                # 任务完成通知脚本
├── create-s5-emulator.js        # 模拟器创建脚本
├── package.json                 # Vela 项目配置
├── src/
│   ├── manifest.json            # Vela 应用配置
│   ├── app.ux                   # 应用入口
│   ├── pages/
│   │   ├── approve/index.ux     # 审批页面
│   │   ├── notify/index.ux      # 通知页面
│   │   └── settings/index.ux    # 设置页面
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

---

## 关键技术点

### 1. 消息推送方案

使用 **ntfy.sh** 作为中间件：
- PC 端脚本发布消息到 ntfy.sh topic
- 手表端通过 `system.fetch` 轮询或 WebSocket 接收消息
- 超时后自动拒绝（Fail-safe 设计）

### 2. Vela 小程序 API

```javascript
// 网络请求
import fetch from '@system.fetch'

// 震动反馈
import vibrator from '@system.vibrator'

// 路由跳转
import router from '@system.router'

// 本地存储
import storage from '@system.storage'
```

### 3. 危险命令检测

复用原项目的正则匹配逻辑：
- `rm -rf`
- `sudo`
- `git push --force`
- `docker rm/prune`
- `terraform destroy`
- 自定义正则规则

### 4. 超时处理

- 默认超时时间：60 秒
- 超时后自动拒绝并通知 PC 端
- 网络异常时退回终端审批

---

## 配置文件示例

### watch.env.example

```bash
# ntfy.sh 配置
NTFY_TOPIC=your-secret-topic-name
NTFY_SERVER=https://ntfy.sh

# 超时配置（秒）
APPROVE_TIMEOUT=60

# 危险命令正则（可选）
DANGEROUS_COMMANDS=rm -rf,sudo,git push --force,docker rm,terraform destroy

# 保护路径（防止 agent 修改）
PROTECTED_PATHS=.claude/hooks/,watch_approve.py,watch_done.py
```

---

## 前置条件

- [x] AIoT IDE 已安装
- [x] Node.js 环境
- [x] 小米 Watch S5 模拟器已创建
- [ ] ntfy.sh 账号（免费）
- [ ] 小米开发者账号（如需真机调试）
- [ ] Claude Code CLI

## 模拟器配置

### 已创建的模拟器

- **名称**: Xiaomi_Watch_S5
- **分辨率**: 480 × 480 px
- **屏幕形状**: 圆形
- **像素密度**: 323 PPI
- **系统镜像**: vela-watch-5.0

### 启动模拟器

1. 在 AIoT IDE 中打开模拟器面板
2. 选择 `Xiaomi_Watch_S5` 模拟器
3. 点击启动按钮
4. 运行 `npm start` 启动应用

---

## 参考资源

- [agent-watch-approve 原项目](https://github.com/ghy196830-del/agent-watch-approve)
- [小米 AIoT 开发者平台](https://iot.mi.com/)
- [ntfy.sh 官网](https://ntfy.sh/)
- [Vela 开发文档](https://iot.mi.com/vela)
- [Claude Code Hooks 文档](https://docs.anthropic.com/claude-code)

---

## 进度记录

| 日期 | 进度 | 备注 |
|------|------|------|
| 2026-06-12 | 项目初始化 | 环境搭建完成，模拟器配置完成 |
| 2026-06-12 | 目录结构 | 完成项目目录结构设计和文件创建 |
| 2026-06-12 | 手表端开发 | 完成审批页面、通知页面、设置页面 |
| 2026-06-12 | PC 端脚本 | 完成 watch_approve.py 和 watch_done.py |

