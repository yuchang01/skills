#!/usr/bin/env python3
"""
Java Code Style Formatter
自动检测Maven环境并执行Spotless代码格式化
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Tuple


class JavaCodeFormatter:
    """Java代码格式化器"""
    
    def __init__(self, project_path: Optional[str] = None):
        """
        初始化格式化器
        
        Args:
            project_path: 项目根目录路径,如果为None则使用当前目录
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.maven_available = False
        self.pom_path = None
    
    def check_maven_installation(self) -> bool:
        """
        检查Maven是否已安装
        
        Returns:
            bool: Maven是否可用
        """
        try:
            result = subprocess.run(
                ["mvn", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ Maven已安装: {result.stdout.splitlines()[0]}")
                self.maven_available = True
                return True
            else:
                return False
        except FileNotFoundError:
            return False
        except subprocess.TimeoutExpired:
            print("⚠ Maven版本检查超时")
            return False
        except Exception as e:
            print(f"⚠ 检查Maven时出错: {e}")
            return False
    
    def find_pom_xml(self) -> Optional[Path]:
        """
        查找pom.xml文件
        首先在指定目录查找,如果不存在则向上搜索父目录
        
        Returns:
            Path: pom.xml的路径,如果未找到则返回None
        """
        current = self.project_path.resolve()
        
        # 向上搜索最多3层
        for _ in range(3):
            pom = current / "pom.xml"
            if pom.exists():
                self.pom_path = current
                return pom
            parent = current.parent
            if parent == current:  # 已到达根目录
                break
            current = parent
        
        return None
    
    def check_spotless_plugin(self) -> bool:
        """
        检查pom.xml中是否配置了Spotless插件
        
        Returns:
            bool: 是否配置了Spotless插件
        """
        if not self.pom_path:
            return False
        
        pom_file = self.pom_path / "pom.xml"
        try:
            content = pom_file.read_text(encoding='utf-8')
            # 简单检查是否包含spotless插件
            if 'spotless-maven-plugin' in content:
                print("✓ 检测到Spotless插件配置")
                return True
            else:
                print("⚠ 未在pom.xml中找到Spotless插件配置")
                return False
        except Exception as e:
            print(f"⚠ 读取pom.xml时出错: {e}")
            return False
    
    def run_spotless_apply(self) -> Tuple[bool, str]:
        """
        运行mvn spotless:apply命令
        
        Returns:
            Tuple[bool, str]: (是否成功, 输出信息)
        """
        if not self.pom_path:
            return False, "未找到pom.xml文件"
        
        print(f"\n正在格式化代码... (项目路径: {self.pom_path})")
        print("执行命令: mvn spotless:apply\n")
        
        try:
            result = subprocess.run(
                ["mvn", "spotless:apply"],
                cwd=self.pom_path,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout
                
        except subprocess.TimeoutExpired:
            return False, "命令执行超时(超过5分钟)"
        except Exception as e:
            return False, f"执行命令时出错: {e}"
    
    def format(self) -> int:
        """
        执行完整的格式化流程
        
        Returns:
            int: 退出码 (0表示成功)
        """
        print("=" * 60)
        print("Java代码格式化工具")
        print("=" * 60)
        
        # 1. 检查Maven
        print("\n[1/4] 检查Maven环境...")
        if not self.check_maven_installation():
            print("\n❌ 错误: 未检测到Maven")
            print("\n请先安装Maven:")
            print("  - Windows: https://maven.apache.org/download.cgi")
            print("  - 或使用包管理器: choco install maven (Chocolatey)")
            print("  - Linux/Mac: 使用包管理器 (apt/yum/brew)")
            print("\n安装后请确保Maven已添加到系统PATH环境变量")
            return 1
        
        # 2. 查找pom.xml
        print("\n[2/4] 查找Maven项目...")
        pom = self.find_pom_xml()
        if not pom:
            print(f"\n❌ 错误: 在 {self.project_path} 及其父目录中未找到pom.xml")
            print("当前不是Maven项目,无法执行格式化")
            return 1
        
        print(f"✓ 找到Maven项目: {self.pom_path}")
        
        # 3. 检查Spotless插件
        print("\n[3/4] 检查Spotless插件配置...")
        has_spotless = self.check_spotless_plugin()
        if not has_spotless:
            print("\n⚠ 警告: 未找到Spotless插件配置")
            print("\n请在pom.xml中添加Spotless插件配置:")
            print("""
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
            """)
            print("\n仍将尝试执行格式化...")
        
        # 4. 执行格式化
        print("\n[4/4] 执行代码格式化...")
        success, output = self.run_spotless_apply()
        
        print("=" * 60)
        if success:
            print("✓ 代码格式化完成!")
            print("=" * 60)
            
            # 提取并显示关键信息
            if "BUILD SUCCESS" in output:
                print("\n格式化结果:")
                for line in output.splitlines():
                    if "Formatted" in line or "spotless" in line.lower():
                        print(f"  {line.strip()}")
            
            return 0
        else:
            print("❌ 代码格式化失败")
            print("=" * 60)
            print("\n错误输出:")
            print(output)
            
            # 提供常见错误的解决建议
            if "spotless" in output.lower() and "plugin" in output.lower():
                print("\n💡 建议: 请检查Spotless插件配置是否正确")
            elif "compilation" in output.lower():
                print("\n💡 建议: 代码存在编译错误,请先修复编译错误")
            
            return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Java代码格式化工具 - 使用Maven Spotless插件自动格式化代码"
    )
    parser.add_argument(
        "--project-path",
        type=str,
        help="指定Maven项目根目录路径(可选,默认使用当前目录)"
    )
    
    args = parser.parse_args()
    
    formatter = JavaCodeFormatter(project_path=args.project_path)
    exit_code = formatter.format()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
