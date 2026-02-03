# Todo Bot 📋

任务管理机器人

## 功能

- 创建和管理待办事项
- 标记任务完成/未完成
- 支持优先级设置
- 每日任务汇总

## 使用方法

```bash
cd todo-bot
python3 todo_bot.py
```

## 命令

- 添加任务：`todo add <任务内容>`
- 完成任务：`todo done <任务ID>`
- 删除任务：`todo delete <任务ID>`
- 查看任务：`todo list`
- 清空完成：`todo clear`

## 输出示例

```
📋 待办事项 - 2026-02-03

✅ 1. [完成] 完成项目报告
⏳ 2. [进行中] 整理文档
📌 3. [高优先级] 回复邮件
...

完成: 1 | 待办: 5
```

## 数据存储

任务数据保存在 `todos.json` 文件中。

## 定时任务

每日汇总：

```bash
# 每天晚上 22 点发送汇总
0 22 * * * cd /path/to/todo-bot && python3 todo_bot.py
```

## 依赖

- Python 3.x
- 无需外部 API

## License

MIT
