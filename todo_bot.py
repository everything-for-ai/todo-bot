#!/usr/bin/env python3
"""
To-Do Bot - AI 待办事项管理
支持：添加/完成/列表、优先级管理、飞书发送
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
SECRET_PATH = Path.home() / ".openclaw" / "secrets" / "feishu_app_secret"
RECEIVER_ID = "ou_a44cdd1c2064d3c9c22242b61ff8b926"


def load_config():
    default = {"todos_file": "todos.json"}
    if Path("config.json").exists():
        with open("config.json") as f:
            default.update(json.load(f))
    return default


def load_openclaw_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def load_secret():
    if SECRET_PATH.exists():
        with open(SECRET_PATH) as f:
            return f.read().strip()
    return None


class TodoBot:
    """待办事项机器人"""
    
    def __init__(self, config_file: str = "todos.json"):
        self.config = load_config()
        self.todos_file = self.config.get("todos_file", "todos.json")
        self.todos = self.load_todos()
    
    def load_todos(self) -> List[Dict]:
        """加载待办"""
        if os.path.exists(self.todos_file):
            with open(self.todos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_todos(self):
        """保存待办"""
        with open(self.todos_file, 'w', encoding='utf-8') as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)
    
    def add(self, task: str, priority: str = "medium", due_date: str = None, category: str = "工作") -> Dict:
        """添加待办"""
        # 检查重复
        for todo in self.todos:
            if todo.get("task", "") == task and todo.get("status") == "pending":
                return {"error": "任务已存在"}
        
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "priority": priority.lower(),
            "category": category,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "completed_at": None
        }
        self.todos.append(todo)
        self.save_todos()
        return todo
    
    def complete(self, todo_id: int) -> Optional[Dict]:
        """完成待办"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["status"] = "completed"
                todo["completed_at"] = datetime.now().isoformat()
                self.save_todos()
                return todo
        return None
    
    def delete(self, todo_id: int) -> bool:
        """删除待办"""
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                self.todos.pop(i)
                self.save_todos()
                return True
        return False
    
    def list_pending(self, category: str = None) -> List[Dict]:
        """列出待办"""
        if category:
            return [t for t in self.todos if t.get("status") == "pending" and t.get("category") == category]
        return [t for t in self.todos if t.get("status") == "pending"]
    
    def list_completed(self, limit: int = 10) -> List[Dict]:
        """列出已完成"""
        completed = [t for t in self.todos if t.get("status") == "completed"]
        return completed[-limit:]
    
    def get_by_priority(self, priority: str) -> List[Dict]:
        """按优先级筛选"""
        return [t for t in self.todos if t.get("status") == "pending" and t.get("priority") == priority.lower()]
    
    def get_overdue(self) -> List[Dict]:
        """逾期待办"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [t for t in self.todos if t.get("status") == "pending" and t.get("due_date") and t.get("due_date") < today]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        pending = [t for t in self.todos if t.get("status") == "pending"]
        completed = [t for t in self.todos if t.get("status") == "completed"]
        
        # 按优先级统计
        by_priority = {"high": 0, "medium": 0, "low": 0}
        for t in pending:
            p = t.get("priority", "medium")
            by_priority[p] = by_priority.get(p, 0) + 1
        
        # 按类别统计
        by_category = {}
        for t in pending:
            c = t.get("category", "其他")
            by_category[c] = by_category.get(c, 0) + 1
        
        return {
            "total": len(self.todos),
            "pending": len(pending),
            "completed": len(completed),
            "by_priority": by_priority,
            "by_category": by_category
        }
    
    def format_message(self) -> str:
        """格式化消息"""
        pending = self.list_pending()
        completed = self.list_completed()
        stats = self.get_stats()
        overdue = self.get_overdue()
        
        message = [f"📋 **待办事项管理** - {datetime.now().strftime('%m/%d %H:%M')}\n"]
        
        # 统计
        message.append(f"📊 **统计:** 共 {stats['total']} 项 | 待办 {stats['pending']} | 已完成 {stats['completed']}\n")
        
        # 逾期
        if overdue:
            message.append(f"⚠️ **逾期 ({len(overdue)} 项):**")
            for t in overdue:
                due = t.get("due_date", "")
                emoji = "🔴" if t.get("priority") == "high" else "🟡"
                message.append(f"   {emoji} {t['task']} (截止: {due})")
            message.append("")
        
        # 按优先级分组
        message.append("🎯 **待办事项 (按优先级):**\n")
        
        for priority in ["high", "medium", "low"]:
            todos = [t for t in pending if t.get("priority") == priority]
            if todos:
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[priority]
                label = {"high": "高优先级", "medium": "中优先级", "low": "低优先级"}[priority]
                
                message.append(f"{emoji} **{label}** ({len(todos)} 项):")
                for i, t in enumerate(todos[:5], 1):
                    cat = t.get("category", "📁")
                    task = t["task"][:35]
                    due = f" 📅{t.get('due_date', '')}" if t.get("due_date") else ""
                    message.append(f"   {i}. {task}{due}")
                    message.append(f"      {cat}")
                message.append("")
        
        # 按类别分组
        message.append("📁 **待办事项 (按类别):**\n")
        
        for cat, count in stats["by_category"].items():
            message.append(f"   📂 {cat}: {count} 项")
        
        message.append("")
        
        # 今日完成
        if completed:
            message.append(f"✅ **最近完成 ({len(completed)} 项):**")
            for t in completed[-3:]:
                completed_at = t.get("completed_at", "")[:16].replace("T", " ")
                message.append(f"   ✓ {t['task'][:40]}")
                message.append(f"      🕐 {completed_at}")
            message.append("")
        
        # 操作提示
        message.append("💡 **操作:**")
        message.append("   添加待办: python3 todo_bot.py add \"任务名称\" [高/中/低] [日期]")
        message.append("   完成待办: python3 todo_bot.py complete [ID]")
        message.append("   删除待办: python3 todo_bot.py delete [ID]")
        message.append("")
        message.append("#待办 #任务管理 #效率")
        
        return "\n".join(message)
    
    def run(self):
        message = self.format_message()
        print(message)
        return message


def get_tenant_access_token(app_id, app_secret):
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    result = resp.json()
    return result.get("tenant_access_token") if result.get("code") == 0 else None


def send_to_feishu(token, receiver_id, content):
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": receiver_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    resp = requests.post(url, params=params, headers=headers, json=data)
    return resp.json().get("code") == 0


def main():
    import sys
    
    bot = TodoBot()
    
    # 命令行操作
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "add" and len(sys.argv) > 2:
            task = sys.argv[2]
            priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
            due_date = sys.argv[4] if len(sys.argv) > 4 else None
            result = bot.add(task, priority, due_date)
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ 已添加: {task}")
                bot.save_todos()
        
        elif cmd == "complete" and len(sys.argv) > 2:
            try:
                todo_id = int(sys.argv[2])
                result = bot.complete(todo_id)
                if result:
                    print(f"✅ 已完成: {result['task']}")
                else:
                    print("❌ 未找到该待办")
            except:
                print("❌ 无效的 ID")
        
        elif cmd == "delete" and len(sys.argv) > 2:
            try:
                todo_id = int(sys.argv[2])
                if bot.delete(todo_id):
                    print(f"✅ 已删除待办 #{todo_id}")
                else:
                    print("❌ 未找到该待办")
            except:
                print("❌ 无效的 ID")
        
        elif cmd == "send":
            # 发送到飞书
            app_config = load_openclaw_config()
            app_id = app_config.get("channels", {}).get("feishu", {}).get("appId")
            app_secret = load_secret()
            
            if app_id and app_secret:
                token = get_tenant_access_token(app_id, app_secret)
                if token:
                    message = bot.format_message()
                    if send_to_feishu(token, RECEIVER_ID, message):
                        print("\n✅ 已发送至飞书！")
                    else:
                        print("\n❌ 发送失败")
            return
    
    # 默认显示列表
    print(f"\n{'='*50}")
    print(f"📋 待办事项管理 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")
    
    message = bot.format_message()
    print(message)


if __name__ == "__main__":
    main()
