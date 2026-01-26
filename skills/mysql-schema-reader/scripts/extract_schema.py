#!/usr/bin/env python3
"""
MySQL Schema Extractor
提取 MySQL 数据库表结构信息，输出为结构化格式供 AI 代码生成使用
"""

import argparse
import json
import sys
import os
import glob
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

try:
    import mysql.connector
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    HAS_MYSQL_CONNECTOR = False

try:
    import MySQLdb
    HAS_MYSQLDB = True
except ImportError:
    HAS_MYSQLDB = False


class MySQLSchemaExtractor:
    """MySQL 表结构提取器"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            if HAS_MYSQL_CONNECTOR:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            elif HAS_MYSQLDB:
                self.connection = MySQLdb.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    passwd=self.password,
                    db=self.database
                )
            else:
                raise ImportError("需要安装 mysql-connector-python 或 pymysql")
            
            print(f"✅ 成功连接到数据库: {self.database}", file=sys.stderr)
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}", file=sys.stderr)
            sys.exit(1)
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
    
    def get_tables(self, table_names: Optional[List[str]] = None) -> List[str]:
        """获取数据库中的表列表"""
        cursor = self.connection.cursor()
        
        if table_names:
            # 验证指定的表是否存在
            placeholders = ','.join(['%s'] * len(table_names))
            query = f"SHOW TABLES LIKE %s" if len(table_names) == 1 else f"SHOW TABLES WHERE Tables_in_{self.database} IN ({placeholders})"
            cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in cursor.fetchall()]
            existing_tables = [t for t in table_names if t in all_tables]
            
            if not existing_tables:
                print(f"⚠️  警告: 指定的表 {table_names} 不存在", file=sys.stderr)
                return []
            
            return existing_tables
        else:
            cursor.execute("SHOW TABLES")
            return [row[0] for row in cursor.fetchall()]
    
    def extract_table_schema(self, table_name: str) -> Dict[str, Any]:
        """提取单个表的结构信息"""
        cursor = self.connection.cursor()
        
        # 获取表注释和存储引擎（MySQL 8.x 兼容）
        cursor.execute(f"""
            SELECT TABLE_COMMENT, ENGINE, TABLE_COLLATION
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (self.database, table_name))
        result = cursor.fetchone()
        table_comment = result[0] or ""
        table_engine = result[1] or "InnoDB"
        table_collation = result[2] or "utf8mb4_unicode_ci"
        
        # 获取列信息
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_KEY,
                COLUMN_DEFAULT,
                EXTRA,
                COLUMN_COMMENT,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, (self.database, table_name))
        
        columns = []
        for row in cursor.fetchall():
            column = {
                "name": row[0],
                "dataType": row[1],
                "columnType": row[2],
                "nullable": row[3] == "YES",
                "key": row[4],  # PRI, UNI, MUL
                "default": row[5],
                "extra": row[6],  # auto_increment, on update CURRENT_TIMESTAMP
                "comment": row[7] or "",
                "maxLength": row[8],
                "precision": row[9],
                "scale": row[10]
            }
            columns.append(column)
        
        # 获取索引信息
        cursor.execute(f"SHOW INDEX FROM `{table_name}`")
        indexes_raw = cursor.fetchall()
        indexes = {}
        
        for row in indexes_raw:
            index_name = row[2]
            if index_name not in indexes:
                indexes[index_name] = {
                    "name": index_name,
                    "unique": row[1] == 0,
                    "type": row[10],
                    "columns": []
                }
            indexes[index_name]["columns"].append(row[4])
        
        # 获取外键信息
        cursor.execute(f"""
            SELECT 
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = %s 
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (self.database, table_name))
        
        foreign_keys = []
        for row in cursor.fetchall():
            foreign_keys.append({
                "name": row[0],
                "column": row[1],
                "referencedTable": row[2],
                "referencedColumn": row[3]
            })
        
        return {
            "tableName": table_name,
            "comment": table_comment,
            "engine": table_engine,
            "collation": table_collation,
            "columns": columns,
            "indexes": list(indexes.values()),
            "foreignKeys": foreign_keys
        }
    
    def extract_schemas(self, table_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """提取数据库表结构"""
        tables = self.get_tables(table_names)
        
        if not tables:
            print("⚠️  未找到任何表", file=sys.stderr)
            return {"database": self.database, "tables": []}
        
        print(f"📊 正在提取 {len(tables)} 个表的结构...", file=sys.stderr)
        
        schemas = []
        for table_name in tables:
            print(f"   - {table_name}", file=sys.stderr)
            schema = self.extract_table_schema(table_name)
            schemas.append(schema)
        
        return {
            "database": self.database,
            "tableCount": len(schemas),
            "tables": schemas
        }


def parse_connection_string(conn_str: str) -> Dict[str, Any]:
    """解析数据库连接字符串
    
    支持格式:
    - mysql://user:password@host:port/database
    - mysql://user:password@host/database
    """
    parsed = urlparse(conn_str)
    
    if parsed.scheme not in ['mysql', 'mysql+pymysql']:
        raise ValueError(f"不支持的连接协议: {parsed.scheme}")
    
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip('/')
    }


def scan_config_files(search_path: str = ".") -> List[str]:
    """扫描项目中的 application-local 配置文件
    
    查找 src/main/resources 和 src/test/resources 目录下的配置文件
    
    Args:
        search_path: 搜索路径，默认为当前目录
    
    Returns:
        找到的配置文件路径列表
    """
    # 搜索 src/main/resources 和 src/test/resources 下的配置文件
    patterns = [
        "**/src/main/resources/application-local.yaml",
        "**/src/main/resources/application-local.yml",
        "**/src/test/resources/application-local.yaml",
        "**/src/test/resources/application-local.yml"
    ]
    
    config_files = []
    for pattern in patterns:
        matches = glob.glob(os.path.join(search_path, pattern), recursive=True)
        config_files.extend(matches)
    
    # 去重并排序
    config_files = sorted(list(set(config_files)))
    return config_files


def parse_yaml_config(config_file: str) -> Optional[Dict[str, Any]]:
    """从 YAML 配置文件解析数据库连接信息
    
    Args:
        config_file: 配置文件路径
    
    Returns:
        数据库连接参数字典，解析失败返回 None
    """
    try:
        import yaml
    except ImportError:
        print("⚠️  需要安装 PyYAML: pip install pyyaml", file=sys.stderr)
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 尝试从 Spring Boot 配置中提取数据库信息
        datasource = None
        if 'spring' in config and 'datasource' in config['spring']:
            datasource = config['spring']['datasource']
        elif 'datasource' in config:
            datasource = config['datasource']
        
        if not datasource:
            print(f"⚠️  配置文件 {config_file} 中未找到数据源配置", file=sys.stderr)
            return None
        
        # 解析 URL 或独立参数
        if 'url' in datasource:
            jdbc_url = datasource['url']
            # 解析 JDBC URL: jdbc:mysql://host:port/database
            if jdbc_url.startswith('jdbc:mysql://'):
                url_part = jdbc_url.replace('jdbc:mysql://', 'mysql://')
                # 移除 URL 参数
                if '?' in url_part:
                    url_part = url_part.split('?')[0]
                
                parsed = urlparse(url_part)
                return {
                    "host": parsed.hostname or "localhost",
                    "port": parsed.port or 3306,
                    "user": datasource.get('username', ''),
                    "password": datasource.get('password', ''),
                    "database": parsed.path.lstrip('/')
                }
        else:
            # 独立参数
            return {
                "host": datasource.get('host', 'localhost'),
                "port": datasource.get('port', 3306),
                "user": datasource.get('username', ''),
                "password": datasource.get('password', ''),
                "database": datasource.get('database', '')
            }
    
    except Exception as e:
        print(f"❌ 解析配置文件失败: {e}", file=sys.stderr)
        return None
    
    return None


def select_config_file(config_files: List[str]) -> Optional[str]:
    """让用户选择一个配置文件
    
    Args:
        config_files: 配置文件路径列表
    
    Returns:
        选中的配置文件路径
    """
    if not config_files:
        return None
    
    if len(config_files) == 1:
        print(f"✅ 找到配置文件: {config_files[0]}", file=sys.stderr)
        return config_files[0]
    
    # 多个配置文件，让用户选择
    print(f"\n📁 找到 {len(config_files)} 个配置文件：", file=sys.stderr)
    for i, file in enumerate(config_files, 1):
        print(f"  [{i}] {file}", file=sys.stderr)
    
    while True:
        try:
            choice = input("\n请选择配置文件 (输入序号): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(config_files):
                selected = config_files[index]
                print(f"✅ 已选择: {selected}", file=sys.stderr)
                return selected
            else:
                print(f"❌ 无效选择，请输入 1-{len(config_files)} 之间的数字", file=sys.stderr)
        except (ValueError, KeyboardInterrupt):
            print("\n❌ 操作已取消", file=sys.stderr)
            return None


def get_cache_path(conn_params: Dict[str, Any], tables: Optional[List[str]] = None) -> str:
    """生成缓存文件路径
    
    Args:
        conn_params: 数据库连接参数
        tables: 表名列表
    
    Returns:
        缓存文件路径
    """
    # 生成缓存键
    cache_key_parts = [
        conn_params['host'],
        str(conn_params['port']),
        conn_params['database']
    ]
    if tables:
        cache_key_parts.extend(sorted(tables))
    
    cache_key = '_'.join(cache_key_parts)
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()[:8]
    
    # 缓存目录
    cache_dir = Path.home() / '.mysql_schema_cache'
    cache_dir.mkdir(exist_ok=True)
    
    filename = f"{conn_params['database']}_{cache_hash}.json"
    return str(cache_dir / filename)


def load_cache(cache_path: str) -> Optional[Dict[str, Any]]:
    """从缓存加载表结构
    
    Args:
        cache_path: 缓存文件路径
    
    Returns:
        缓存的表结构数据，不存在返回 None
    """
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 从缓存加载: {cache_path}", file=sys.stderr)
        return data
    except Exception as e:
        print(f"⚠️  缓存加载失败: {e}", file=sys.stderr)
        return None


def save_cache(cache_path: str, data: Dict[str, Any]):
    """保存表结构到缓存
    
    Args:
        cache_path: 缓存文件路径
        data: 表结构数据
    """
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已缓存到: {cache_path}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  缓存保存失败: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="提取 MySQL 数据库表结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用连接字符串提取所有表
  python extract_schema.py --url "mysql://user:pass@localhost:3306/mydb"
  
  # 使用独立参数提取所有表
  python extract_schema.py --host localhost --user root --password 123456 --database mydb
  
  # 扫描并选择配置文件
  python extract_schema.py --scan-config /path/to/project
  
  # 仅提取指定的表
  python extract_schema.py --url "mysql://user:pass@localhost/mydb" --tables users orders
  
  # 使用缓存（默认启用）
  python extract_schema.py --url "mysql://user:pass@localhost/mydb" --cache
  
  # 强制刷新，忽略缓存
  python extract_schema.py --url "mysql://user:pass@localhost/mydb" --force-refresh
  
  # 输出为 Markdown 格式
  python extract_schema.py --url "mysql://user:pass@localhost/mydb" --format markdown
        """
    )
    
    # 连接参数
    conn_group = parser.add_mutually_exclusive_group(required=False)
    conn_group.add_argument('--url', help='数据库连接字符串 (mysql://user:password@host:port/database)')
    conn_group.add_argument('--host', help='数据库主机地址')
    conn_group.add_argument('--scan-config', metavar='PATH', help='扫描项目中的 application-local 配置文件')
    
    parser.add_argument('--port', type=int, default=3306, help='数据库端口 (默认: 3306)')
    parser.add_argument('--user', help='数据库用户名')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--database', help='数据库名称')
    
    # 提取选项
    parser.add_argument('--tables', nargs='+', help='指定要提取的表名 (默认: 所有表)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', 
                       help='输出格式 (默认: json)')
    parser.add_argument('--output', '-o', help='输出文件路径 (默认: 标准输出)')
    parser.add_argument('--pretty', action='store_true', help='JSON 格式化输出')
    
    # 缓存选项
    parser.add_argument('--cache', action='store_true', help='启用缓存（默认启用）')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存')
    parser.add_argument('--force-refresh', action='store_true', help='强制刷新，忽略缓存重新提取')
    
    args = parser.parse_args()
    
    # 解析连接参数
    conn_params = None
    
    if args.scan_config:
        # 扫描配置文件模式
        print(f"🔍 扫描配置文件: {args.scan_config}", file=sys.stderr)
        config_files = scan_config_files(args.scan_config)
        
        if not config_files:
            print("❌ 未找到 application-local.yaml/yml 配置文件", file=sys.stderr)
            sys.exit(1)
        
        selected_config = select_config_file(config_files)
        if not selected_config:
            sys.exit(1)
        
        conn_params = parse_yaml_config(selected_config)
        if not conn_params:
            print("❌ 无法从配置文件解析数据库连接信息", file=sys.stderr)
            sys.exit(1)
    
    elif args.url:
        conn_params = parse_connection_string(args.url)
    
    elif args.host:
        if not all([args.user, args.password, args.database]):
            parser.error("使用独立参数时，必须提供 --user, --password, --database")
        conn_params = {
            "host": args.host,
            "port": args.port,
            "user": args.user,
            "password": args.password,
            "database": args.database
        }
    
    else:
        parser.error("必须提供数据库连接方式：--url、--host 或 --scan-config")
    
    # 检查缓存设置
    use_cache = not args.no_cache  # 默认启用缓存
    force_refresh = args.force_refresh
    
    # 尝试从缓存加载
    result = None
    cache_path = None
    
    if use_cache and not force_refresh:
        cache_path = get_cache_path(conn_params, args.tables)
        result = load_cache(cache_path)
        
        if result:
            print("💾 使用缓存的表结构数据", file=sys.stderr)
            print("💡 提示: 使用 --force-refresh 可强制重新提取最新表结构", file=sys.stderr)
    
    # 如果没有缓存或强制刷新，则连接数据库提取
    if result is None:
        if force_refresh:
            print("🔄 强制刷新模式，重新提取表结构...", file=sys.stderr)
        
        # 提取表结构
        extractor = MySQLSchemaExtractor(**conn_params)
        extractor.connect()
        
        try:
            result = extractor.extract_schemas(args.tables)
            
            # 保存到缓存
            if use_cache:
                if cache_path is None:
                    cache_path = get_cache_path(conn_params, args.tables)
                save_cache(cache_path, result)
        
        finally:
            extractor.close()
    
    # 格式化输出
    try:
        
        if args.format == 'json':
            output = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
        else:  # markdown
            output = format_as_markdown(result)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 表结构已保存到: {args.output}", file=sys.stderr)
        else:
            print(output)
    
    except Exception as e:
        print(f"❌ 处理失败: {e}", file=sys.stderr)
        sys.exit(1)


def format_as_markdown(schema_data: Dict[str, Any]) -> str:
    """将表结构格式化为 Markdown"""
    lines = [f"# Database: {schema_data['database']}\n"]
    lines.append(f"**表数量**: {schema_data['tableCount']}\n")
    
    for table in schema_data['tables']:
        lines.append(f"## {table['tableName']}")
        if table['comment']:
            lines.append(f"**说明**: {table['comment']}\n")
        else:
            lines.append("")
        
        # 字段信息
        lines.append("### 字段")
        lines.append("| 字段名 | 类型 | 可空 | 键 | 默认值 | 说明 |")
        lines.append("|--------|------|------|-----|--------|------|")
        
        for col in table['columns']:
            key = col['key'] if col['key'] else '-'
            default = col['default'] if col['default'] is not None else '-'
            nullable = '是' if col['nullable'] else '否'
            comment = col['comment'] if col['comment'] else '-'
            lines.append(f"| {col['name']} | {col['columnType']} | {nullable} | {key} | {default} | {comment} |")
        
        # 索引信息
        if table['indexes']:
            lines.append("\n### 索引")
            lines.append("| 索引名 | 类型 | 唯一 | 列 |")
            lines.append("|--------|------|------|-----|")
            for idx in table['indexes']:
                unique = '是' if idx['unique'] else '否'
                columns = ', '.join(idx['columns'])
                lines.append(f"| {idx['name']} | {idx['type']} | {unique} | {columns} |")
        
        # 外键信息
        if table['foreignKeys']:
            lines.append("\n### 外键")
            lines.append("| 约束名 | 列 | 引用表 | 引用列 |")
            lines.append("|--------|-----|--------|--------|")
            for fk in table['foreignKeys']:
                lines.append(f"| {fk['name']} | {fk['column']} | {fk['referencedTable']} | {fk['referencedColumn']} |")
        
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
