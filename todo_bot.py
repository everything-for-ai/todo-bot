#!/usr/bin/env python3
"""
To-Do Bot - AI-powered task management
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional


class TodoBot:
    def __init__(self, config_file: str = "todos.json"):
        self.config_file = config_file
        self.todos = self.load_todos()
    
    def load_todos(self) -> List[Dict]:
        """Load todos from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_todos(self):
        """Save todos to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)
    
    def add(self, task: str, priority: str = "medium", due_date: str = None):
        """Add a new todo"""
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "completed_at": None
        }
        self.todos.append(todo)
        self.save_todos()
        return todo
    
    def complete(self, todo_id: int) -> Optional[Dict]:
        """Mark todo as completed"""
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["status"] = "completed"
                todo["completed_at"] = datetime.now().isoformat()
                self.save_todos()
                return todo
        return None
    
    def list_pending(self) -> List[Dict]:
        """List all pending todos"""
        return [t for t in self.todos if t["status"] == "pending"]
    
    def list_completed(self) -> List[Dict]:
        """List all completed todos"""
        return [t for t in self.todos if t["status"] == "completed"]
    
    def get_summary(self) -> str:
        """Get todo summary"""
        pending = self.list_pending()
        completed = self.list_completed()
        
        return f"""
📋 待办事项摘要

待办 ({len(pending)}):
{chr(10).join([f'- [{t["priority"][0].upper()}] {t["task"]}' for t in pending[:10]]) or '暂无待办'}

已完成 ({len(completed)}):
{chr(10).join([f'✓ {t["task"]}' for t in completed[-5:]]) or '暂无完成项'}
        """.strip()
    
    def run(self):
        print(self.get_summary())
        return self.get_summary()


if __name__ == "__main__":
    bot = TodoBot()
    bot.run()
