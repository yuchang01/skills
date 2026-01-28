#!/usr/bin/env python3
"""
AI Interaction Recorder
记录AI对话的核心脚本，用于生成结构化的对话记录文件
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class ConversationRecorder:
    """对话记录器"""
    
    def __init__(self, records_dir: str = "records"):
        """
        初始化记录器
        
        Args:
            records_dir: 记录存储的根目录
        """
        self.records_dir = Path(records_dir)
        self.by_topic_dir = self.records_dir / "by-topic"
        self.by_concept_dir = self.records_dir / "by-concept"
        self.index_file = self.records_dir / "index.md"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.by_topic_dir.mkdir(parents=True, exist_ok=True)
        self.by_concept_dir.mkdir(parents=True, exist_ok=True)
    
    def record_conversation(
        self,
        title: str,
        question: str,
        answer: str,
        code_snippets: List[Dict[str, str]] = None,
        topic: str = "",
        tags: List[str] = None,
        difficulty: str = "进阶",
        problem_type: str = "概念理解"
    ) -> str:
        """
        记录一次对话
        
        Args:
            title: 对话标题
            question: 用户的问题
            answer: AI的回答
            code_snippets: 代码片段列表 [{"language": "java", "code": "...", "description": "..."}]
            topic: 技术主题 (如 spring-statemachine)
            tags: 知识点标签列表
            difficulty: 难度等级 (入门/进阶/高级)
            problem_type: 问题类型
            
        Returns:
            生成的文件路径
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        filename_timestamp = timestamp.strftime("%Y%m%d-%H%M%S")
        
        # 生成文件名
        safe_title = self._sanitize_filename(title)
        filename = f"{topic}-{safe_title}-{filename_timestamp}.md"
        
        # 确定保存路径
        topic_dir = self.by_topic_dir / topic
        topic_dir.mkdir(exist_ok=True)
        file_path = topic_dir / filename
        
        # 生成文件内容
        content = self._generate_content(
            title=title,
            date=date_str,
            topic=topic,
            tags=tags or [],
            difficulty=difficulty,
            problem_type=problem_type,
            question=question,
            answer=answer,
            code_snippets=code_snippets or []
        )
        
        # 写入文件
        file_path.write_text(content, encoding='utf-8')
        
        # 更新索引
        self._update_index(title, topic, tags, str(file_path.relative_to(self.records_dir)))
        
        return str(file_path)
    
    def _sanitize_filename(self, title: str) -> str:
        """清理文件名，移除特殊字符"""
        # 移除特殊字符，替换为连字符
        safe = re.sub(r'[^\w\s-]', '', title)
        safe = re.sub(r'[-\s]+', '-', safe)
        return safe.lower()[:50]  # 限制长度
    
    def _generate_content(
        self,
        title: str,
        date: str,
        topic: str,
        tags: List[str],
        difficulty: str,
        problem_type: str,
        question: str,
        answer: str,
        code_snippets: List[Dict[str, str]]
    ) -> str:
        """生成Markdown内容"""
        
        tags_yaml = "\n".join([f"  - {tag}" for tag in tags])
        
        content = f"""---
title: {title}
date: {date}
topic: {topic}
tags:
{tags_yaml}
difficulty: {difficulty}
problem_type: {problem_type}
---

## 对话概要

[AI自动生成：一句话总结对话的核心内容]

## 核心问题

### 原始提问
```
{question}
```

### 问题背景
- **触发场景：** [用户在什么情况下遇到这个问题]
- **问题类型：** {problem_type}
- **技术栈：** {topic}

## AI解答

{answer}

"""
        
        # 添加代码片段
        if code_snippets:
            content += "### 代码示例\n\n"
            for idx, snippet in enumerate(code_snippets, 1):
                lang = snippet.get('language', 'text')
                code = snippet.get('code', '')
                desc = snippet.get('description', f'示例{idx}')
                
                content += f"#### {desc}\n```{lang}\n{code}\n```\n\n"
        
        content += """
## 知识点标签

### 主分类
- **技术栈：** {topic}
- **难度：** {difficulty}

### 关键概念
{tag_list}

## 延伸学习

### 相关对话
- [待补充] 相关对话链接

### 推荐资源
- 📖 官方文档：[待补充]
- 💻 代码示例：[待补充]

---

*本记录由AI交互记录助手自动生成于 {date}*
""".format(
            topic=topic,
            difficulty=difficulty,
            tag_list="\n".join([f"- {tag}" for tag in tags]),
            date=date
        )
        
        return content
    
    def _update_index(self, title: str, topic: str, tags: List[str], file_path: str):
        """更新索引文件"""
        # 简化版：追加到索引文件
        if not self.index_file.exists():
            self.index_file.write_text("# AI交互记录索引\n\n## 最近记录\n\n", encoding='utf-8')
        
        with open(self.index_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            tags_str = ", ".join(tags[:3]) if tags else "无标签"
            f.write(f"- [{title}]({file_path}) - {topic} - {tags_str} - {timestamp}\n")


def main():
    """示例用法"""
    recorder = ConversationRecorder()
    
    # 示例：记录一次关于Spring状态机的对话
    file_path = recorder.record_conversation(
        title="Spring状态机 - Guard条件 - 复杂业务逻辑判断",
        question="Spring状态机的Guard条件怎么写？我需要在订单支付时检查库存和用户余额。",
        answer="Guard条件用于在状态转换前进行条件判断...",
        code_snippets=[
            {
                "language": "java",
                "code": "builder.externalTransition()\n    .from(OrderState.CREATED)\n    .to(OrderState.PAID)\n    .on(OrderEvent.PAY)\n    .when(ctx -> checkStock(ctx) && checkBalance(ctx));",
                "description": "Guard条件示例"
            }
        ],
        topic="spring-statemachine",
        tags=["Guard条件", "条件判断", "最佳实践"],
        difficulty="进阶",
        problem_type="代码实现"
    )
    
    print(f"✅ 对话已记录到：{file_path}")


if __name__ == "__main__":
    main()
