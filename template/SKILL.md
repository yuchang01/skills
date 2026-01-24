---
name: [skill-name]
description: "[一句话描述核心功能]。当 AI 需要 [触发场景 1]、[触发场景 2] 或处理涉及 [关键对象/技术] 的任务时使用。触发词：关键词1, 关键词2, 关键词3。"
license: "Proprietary. See LICENSE.txt for terms."
compatibility: "Optional: e.g., Requires Python 3.10+, Node.js 18+, or specific CLI tools."
metadata:
  version: "1.0.0"
  author: "Agent Skills Team"
  category: "[Category: e.g., Document Processing, Technical, Creative]"
---

# [Skill Title]

## 🎯 概览 (Overview)
[简要说明该技能的核心价值和目标。避免冗余，直击重点。]

## 🛠️ 何时使用 (When to Use)
- **场景 A**: [具体描述]
- **场景 B**: [具体描述]
- **限制**: [说明该技能不适用的场景，防止滥用]

## 🚀 工作流 (Workflows)

### 决策树 (Decision Tree)
1. **[条件 1]** -> 执行 [工作流 A]
2. **[条件 2]** -> 执行 [工作流 B]
3. **[特殊情况]** -> 参考 [资源文件]

### [工作流 A]: [名称]
1. **准备阶段**:
   - **强制阅读**: 读取 `references/[file].md` 以获取完整规范。**严禁设置读取范围限制**。
   - 检查环境依赖。
2. **执行步骤**:
   - 步骤 1: [具体指令，使用祈使句]
   - 步骤 2: [条件分支示例] 如果 [条件]，则 [动作]；否则 [动作]。
3. **验证阶段**:
   - [具体的验证方法或脚本]

---

## 📂 资源与目录指南 (Directory Usage)
- `scripts/`: 包含可执行脚本（Python/Node.js）。优先调用脚本处理复杂逻辑，保持 `SKILL.md` 简洁。
- `references/`: 存放详尽的 API 文档、规范或长篇教程。利用**渐进式披露** (Progressive Disclosure)，仅在需要时引导 AI 读取。
- `assets/`: 存放静态模板、示例文件或原始资源（如图片、Schema）。

## 💡 最佳实践与原则 (Best Practices)
- **简洁性原则**: `SKILL.md` 应作为导航站而非百科全书。复杂的实现细节应移至 `references/`。
- **自适应自由度**: 在指令中明确哪些步骤必须严格执行（如安全性、核心流程），哪些步骤允许 AI 根据具体情况进行创造性发挥（如代码优化、文案润色）。
- **上下文敏感**: 意识到上下文窗口限制，只提供执行任务必不可少的信息。
- **精确指令**: 使用“读取”、“运行”、“验证”等明确动词。
- **错误处理**: 预判常见错误（如依赖缺失、路径错误）并提供解决方案。

## ⚙️ 依赖项 (Dependencies)
- [工具名称] (版本要求)
- [库/模块] (安装命令)

---
*生成的 SKILL.md 应遵循此模板，确保不同 AI 工具均能快速识别场景并准确执行任务。*
