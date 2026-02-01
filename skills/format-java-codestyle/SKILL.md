---
name: format-java-codestyle
description: "自动格式化Java代码风格。当AI生成Java代码或用户提交Java代码时,自动运行mvn spotless:apply进行代码格式化。触发词:格式化Java代码,spotless,代码风格,code style,format Java。"
license: "Proprietary. See LICENSE.txt for terms."
compatibility: "Requires Maven 3.x+. Project must have Spotless plugin configured in pom.xml."
metadata:
  version: "1.0.0"
  author: "Agent Skills Team"
  category: "Technical"
---

# Java Code Style Formatter

## 🎯 概览 (Overview)
自动检测并执行Java代码格式化,确保代码风格一致性。该技能在AI完成Java代码生成后自动触发,使用Maven Spotless插件对代码进行格式化。

## 🛠️ 何时使用 (When to Use)
- **Java代码生成后**: AI助理完成Java代码生成并提供给用户时
- **代码提交前**: 用户提交Java代码需要格式化时
- **代码风格检查**: 需要统一代码风格和格式化规范时
- **限制**: 
  - 项目必须是Maven项目(包含pom.xml)
  - 项目必须已配置Spotless插件
  - 不适用于非Java项目或Gradle项目

## 🚀 工作流 (Workflows)

### 决策树 (Decision Tree)
1. **检测到Java代码生成/修改** -> 执行 [自动格式化工作流]
2. **用户显式请求格式化** -> 执行 [手动格式化工作流]
3. **Maven不可用** -> 显示安装提示

### [自动格式化工作流]: Java代码格式化
1. **环境检测阶段**:
   - 检测当前目录是否存在`pom.xml`文件,确认为Maven项目
   - 执行`mvn --version`命令验证Maven是否已安装
   - 如果Maven不可用,显示提示: "当前环境中未检测到Maven,请先安装Maven以使用代码格式化功能"并终止流程

2. **格式化执行阶段**:
   - 调用`scripts/format_code.py`脚本自动执行格式化
   - 脚本将运行`mvn spotless:apply`命令
   - 等待命令执行完成

3. **结果反馈阶段**:
   - 如果格式化成功,向用户反馈: "✓ 代码格式化完成"
   - 如果格式化失败(如Spotless插件未配置),显示错误信息并提供解决建议
   - 列出被格式化的文件清单(如果可用)

### [手动格式化工作流]: 用户主动请求格式化
1. **确认项目类型**:
   - 询问用户是否为Maven项目
   - 确认pom.xml位置

2. **执行格式化**:
   - 切换到项目根目录
   - 运行`python scripts/format_code.py`
   - 或直接运行`python scripts/format_code.py --project-path <指定路径>`

3. **报告结果**:
   - 展示格式化结果和统计信息

---

## 📂 资源与目录指南 (Directory Usage)
- `scripts/format_code.py`: 核心格式化脚本,负责环境检测和命令执行

## 💡 最佳实践与原则 (Best Practices)
- **自动触发**: AI在完成Java代码生成后应主动执行此技能,无需用户明确请求
- **静默执行**: 格式化过程应在后台执行,不打断用户交互流程
- **错误提示友好**: 当环境不满足条件时,提供清晰的安装指引或配置建议
- **项目识别**: 优先在当前工作目录查找pom.xml,如不存在则向上级目录搜索
- **批量格式化**: 支持对整个项目的Java文件进行批量格式化

## ⚙️ 依赖项 (Dependencies)
- Maven 3.x+ (必须安装并配置在系统PATH中)
- Spotless Maven Plugin (必须在项目pom.xml中配置)
- Python 3.7+ (用于运行格式化脚本)

## 🔧 Spotless配置示例
项目的pom.xml应包含类似以下配置:
```xml
<plugin>
    <groupId>com.diffplug.spotless</groupId>
    <artifactId>spotless-maven-plugin</artifactId>
    <version>3.2.1</version>
    <configuration>
        <formats>
            <!-- you can define as many formats as you want, each is independent -->
            <format>
                <!-- define the files to apply to -->
                <includes>
                    <include>.gitattributes</include>
                    <include>.gitignore</include>
                </includes>
                <!-- define the steps to apply to those files -->
                <trimTrailingWhitespace/>
                <endWithNewline/>
                <indent>
                    <tabs>true</tabs>
                    <spacesPerTab>4</spacesPerTab>
                </indent>
            </format>
        </formats>
        <java>
            <toggleOffOn><off>fmt:off</off><on>fmt:on</on></toggleOffOn>
            <!-- These are the defaults, you can override if you want -->
            <includes>
                <include>src/main/java/**/*.java</include>
                <include>src/test/java/**/*.java</include>
            </includes>

            <palantirJavaFormat>
                <version>2.86.0</version>
            </palantirJavaFormat>

            <removeUnusedImports/>
        </java>
    </configuration>
</plugin>
```

## ❗ 故障排除 (Error Handling)
- **Maven未安装**: 显示安装链接和指引
- **pom.xml不存在**: 提示当前不是Maven项目
- **Spotless插件未配置**: 提供配置示例和文档链接
- **格式化失败**: 展示Maven错误输出,协助用户定位问题

---
*该技能遵循Agent Skills规范,确保在不同AI工具中均能准确识别和执行。*
