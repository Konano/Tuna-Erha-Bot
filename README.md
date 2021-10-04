# Tuna Erha Bot

Erha-Bot Tuna 特供版

## 目前指令

可用：

- /weather - 显示清华大学天气（彩云 API）
- /forecast - 降雨分钟级预报
- /forecast_hourly - 天气小时级预报
- /mute - 屏蔽发布源
- /unmute - 解除屏蔽发布源
- /mute_list - 列出所有被屏蔽的发布源
- /roll - 从 1 开始的随机数
- /callpolice - 在线报警
- /status - Bot 连接状态
- /washer - 洗衣机在线状态
- /register - 一键注册防止失学
- /hitreds - 一键打红人
- /help - 可用指令说明
- /echo - 回显消息到群 (owner)

废弃：

- /libseat - 查看文图座位剩余情况
- /weather_thu - 显示学校区域当前的天气（学校天气站）
- /weather_today - 显示当前位置的今日天气预报（彩云）

## Usage

```bash
cp config-sample.ini config.ini
vi config.ini
pm2 start ecosystem.config.js
```
