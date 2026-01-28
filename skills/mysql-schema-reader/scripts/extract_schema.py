#!/usr/bin/env python3
"""
MySQL Schema Extractor
提取 MySQL 数据库表结构信息，输出为结构化格式供分析和文档使用
"""

import argparse
import json
import sys
import os
import glob
import hashlib
import tempfile
from datetime import datetime
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
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str, max_retries: int = 3, timeout: int = 10):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.max_retries = max_retries
        self.timeout = timeout
        
    def connect(self):
        """建立数据库连接（带重试机制）"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if HAS_MYSQL_CONNECTOR:
                    self.connection = mysql.connector.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        connection_timeout=self.timeout
                    )
                elif HAS_MYSQLDB:
                    self.connection = MySQLdb.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        passwd=self.password,
                        db=self.database,
                        connect_timeout=self.timeout
                    )
                else:
                    raise ImportError("需要安装 mysql-connector-python 或 pymysql")
                
                print(f"✅ 成功连接到数据库: {self.database}", file=sys.stderr)
                return
                
            except ImportError as e:
                # 依赖问题不重试
                print(f"❌ 缺少必要的 Python 包: {e}", file=sys.stderr)
                print(f"💡 请安装: pip install mysql-connector-python pyyaml", file=sys.stderr)
                sys.exit(1)
                
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    print(f"⚠️  连接失败 (尝试 {attempt}/{self.max_retries}): {e}", file=sys.stderr)
                    print(f"🔄 {2 ** (attempt - 1)} 秒后重试...", file=sys.stderr)
                    import time
                    time.sleep(2 ** (attempt - 1))  # 指数退避: 1s, 2s, 4s
                else:
                    print(f"❌ 数据库连接失败 (已重试 {self.max_retries} 次)", file=sys.stderr)
                    self._print_connection_diagnostics(e)
        
        sys.exit(1)
    
    def _print_connection_diagnostics(self, error: Exception):
        """打印连接失败的诊断信息"""
        error_msg = str(error).lower()
        
        print(f"\n🔍 错误详情: {error}", file=sys.stderr)
        print(f"\n💡 可能的原因和解决方案:", file=sys.stderr)
        
        if 'access denied' in error_msg or '1045' in error_msg:
            print(f"   ❌ 用户名或密码错误", file=sys.stderr)
            print(f"      - 检查用户名: {self.user}", file=sys.stderr)
            print(f"      - 验证密码是否正确", file=sys.stderr)
            print(f"      - 确认数据库用户权限: GRANT ALL ON {self.database}.* TO '{self.user}'@'%'", file=sys.stderr)
        
        elif 'unknown database' in error_msg or '1049' in error_msg:
            print(f"   ❌ 数据库不存在: {self.database}", file=sys.stderr)
            print(f"      - 检查数据库名称拼写", file=sys.stderr)
            print(f"      - 查看可用数据库: SHOW DATABASES", file=sys.stderr)
        
        elif 'can\'t connect' in error_msg or 'connection refused' in error_msg or '2003' in error_msg:
            print(f"   ❌ 无法连接到数据库服务器", file=sys.stderr)
            print(f"      - 检查主机地址: {self.host}:{self.port}", file=sys.stderr)
            print(f"      - 确认 MySQL 服务正在运行", file=sys.stderr)
            print(f"      - 检查防火墙设置", file=sys.stderr)
            print(f"      - 验证网络连接: ping {self.host}", file=sys.stderr)
        
        elif 'timeout' in error_msg or 'timed out' in error_msg:
            print(f"   ❌ 连接超时", file=sys.stderr)
            print(f"      - 网络延迟过高或服务器响应慢", file=sys.stderr)
            print(f"      - 尝试增加超时时间（当前: {self.timeout}秒）", file=sys.stderr)
            print(f"      - 检查网络连接稳定性", file=sys.stderr)
        
        elif 'host' in error_msg and 'not allowed' in error_msg:
            print(f"   ❌ 主机不允许连接", file=sys.stderr)
            print(f"      - MySQL 用户权限限制了连接来源", file=sys.stderr)
            print(f"      - 需要授权: GRANT ALL ON *.* TO '{self.user}'@'你的IP' IDENTIFIED BY 'password'", file=sys.stderr)
        
        else:
            print(f"   ❌ 未知错误", file=sys.stderr)
            print(f"      - 检查 MySQL 服务日志", file=sys.stderr)
            print(f"      - 验证数据库配置", file=sys.stderr)
    
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
    
    def get_server_version(self) -> str:
        """获取数据库服务器版本"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            return version
        except Exception:
            return "unknown"
    
    def extract_schemas(self, table_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """提取数据库表结构"""
        tables = self.get_tables(table_names)
        
        if not tables:
            print("⚠️  未找到任何表", file=sys.stderr)
            return {
                "database": self.database,
                "tables": [],
                "metadata": self._get_metadata()
            }
        
        print(f"📊 正在提取 {len(tables)} 个表的结构...", file=sys.stderr)
        
        schemas = []
        for table_name in tables:
            print(f"   - {table_name}", file=sys.stderr)
            schema = self.extract_table_schema(table_name)
            schemas.append(schema)
        
        return {
            "database": self.database,
            "tableCount": len(schemas),
            "tables": schemas,
            "metadata": self._get_metadata()
        }
    
    def _get_metadata(self) -> Dict[str, Any]:
        """生成元数据信息"""
        return {
            "extractedAt": datetime.now().isoformat(),
            "serverVersion": self.get_server_version(),
            "host": self.host,
            "port": self.port,
            "extractorVersion": "2.0.0"
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


def select_config_file(config_files: List[str], target_database: Optional[str] = None) -> Optional[str]:
    """尝试自动选择配置文件，如果不唯一则列出选项
    
    Args:
        config_files: 配置文件路径列表
        target_database: 目标数据库名称，用于智能匹配
    
    Returns:
        选中的配置文件路径，若不唯一则返回 None
    """
    if not config_files:
        return None
    
    if len(config_files) == 1:
        print(f"✅ 找到配置文件: {config_files[0]}", file=sys.stderr)
        return config_files[0]
    
    # 如果指定了目标数据库，尝试智能匹配
    if target_database:
        print(f"🔍 尝试匹配数据库: {target_database}", file=sys.stderr)
        matched_configs = []
        
        for config_file in config_files:
            conn_params = parse_yaml_config(config_file)
            if conn_params and conn_params.get('database') == target_database:
                matched_configs.append(config_file)
        
        if len(matched_configs) == 1:
            print(f"✅ 自动匹配到配置文件: {matched_configs[0]}", file=sys.stderr)
            return matched_configs[0]
        elif len(matched_configs) > 1:
            print(f"⚠️  找到 {len(matched_configs)} 个匹配的配置文件", file=sys.stderr)
            config_files = matched_configs
        elif len(matched_configs) == 0:
            print(f"⚠️  未找到数据库 '{target_database}' 的配置文件", file=sys.stderr)
    
    # 不唯一且无法自动匹配，列出选项供 AI 决策
    print(f"\n📁 找到多个配置文件，请指定 --config <路径> 或 --database <名称>：", file=sys.stderr)
    for i, file in enumerate(config_files, 1):
        conn_params = parse_yaml_config(file)
        db_name = conn_params.get('database', '未知') if conn_params else '未知'
        print(f"  - {file} (database: {db_name})", file=sys.stderr)
    
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
    
    # 使用项目根目录下的 .aiout/mysql-schema-reader/cache/
    cache_dir = Path.cwd() / '.aiout' / 'mysql-schema-reader' / 'cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{conn_params['database']}_{cache_hash}.json"
    return str(cache_dir / filename)


def load_cache(cache_path: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
    """从缓存加载表结构
    
    Args:
        cache_path: 缓存文件路径
        max_age_hours: 缓存最大有效期（小时），0表示不限制
    
    Returns:
        缓存的表结构数据，不存在或过期返回 None
    """
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查缓存是否包含元数据
        if 'metadata' not in data:
            print(f"⚠️  缓存格式过旧，需要重新提取", file=sys.stderr)
            return None
        
        # 检查缓存时效性
        if max_age_hours > 0:
            extracted_at = datetime.fromisoformat(data['metadata']['extractedAt'])
            age_hours = (datetime.now() - extracted_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                print(f"⚠️  缓存已过期 ({age_hours:.1f} 小时)，需要重新提取", file=sys.stderr)
                return None
        
        extracted_time = data['metadata']['extractedAt']
        server_version = data['metadata'].get('serverVersion', 'unknown')
        print(f"✅ 从缓存加载: {cache_path}", file=sys.stderr)
        print(f"   提取时间: {extracted_time}", file=sys.stderr)
        print(f"   数据库版本: {server_version}", file=sys.stderr)
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
        
        extracted_time = data.get('metadata', {}).get('extractedAt', 'unknown')
        print(f"✅ 已缓存到: {cache_path}", file=sys.stderr)
        print(f"   缓存时间: {extracted_time}", file=sys.stderr)
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
    conn_group.add_argument('--config', metavar='FILE', help='直接指定配置文件路径')
    
    parser.add_argument('--port', type=int, default=3306, help='数据库端口 (默认: 3306)')
    parser.add_argument('--user', help='数据库用户名')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--database', help='数据库名称（用于智能匹配配置文件或覆盖配置）')
    
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
    parser.add_argument('--cache-max-age', type=int, default=24, help='缓存最大有效期（小时），默认24小时，0表示不限制')
    
    # 连接选项
    parser.add_argument('--max-retries', type=int, default=3, help='连接失败最大重试次数（默认: 3）')
    parser.add_argument('--timeout', type=int, default=10, help='连接超时时间（秒，默认: 10）')
    
    args = parser.parse_args()
    
    # 解析连接参数
    conn_params = None
    
    if args.config:
        # 直接指定配置文件模式
        conn_params = parse_yaml_config(args.config)
        if not conn_params:
            print(f"❌ 无法从配置文件解析数据库连接信息: {args.config}", file=sys.stderr)
            sys.exit(1)
        # 如果命令行指定了 --database，覆盖配置文件中的数据库名
        if args.database:
            conn_params['database'] = args.database

    elif args.scan_config:
        # 扫描配置文件模式
        print(f"🔍 扫描配置文件: {args.scan_config}", file=sys.stderr)
        config_files = scan_config_files(args.scan_config)
        
        if not config_files:
            print("❌ 未找到 application-local.yaml/yml 配置文件", file=sys.stderr)
            sys.exit(1)
        
        selected_config = select_config_file(config_files, args.database)
        if not selected_config:
            # 如果不唯一，打印信息后退出，由 AI 处理
            sys.exit(1)
        
        conn_params = parse_yaml_config(selected_config)
        if not conn_params:
            print("❌ 无法从配置文件解析数据库连接信息", file=sys.stderr)
            sys.exit(1)
        
        # 如果命令行指定了 --database，覆盖配置文件中的数据库名
        if args.database:
            conn_params['database'] = args.database
    
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
        result = load_cache(cache_path, args.cache_max_age)
        
        if result:
            print("💾 使用缓存的表结构数据", file=sys.stderr)
            print("💡 提示: 使用 --force-refresh 可强制重新提取最新表结构", file=sys.stderr)
    
    # 如果没有缓存或强制刷新，则连接数据库提取
    if result is None:
        if force_refresh:
            print("🔄 强制刷新模式，重新提取表结构...", file=sys.stderr)
        
        # 提取表结构
        extractor = MySQLSchemaExtractor(
            **conn_params,
            max_retries=args.max_retries,
            timeout=args.timeout
        )
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
            output_path = args.output
        else:
            # 默认输出到项目根目录的 .aiout/mysql-schema-reader/outputs/
            output_dir = Path.cwd() / '.aiout' / 'mysql-schema-reader' / 'outputs'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            ext = 'json' if args.format == 'json' else 'md'
            filename = f"{conn_params['database']}.{ext}"
            output_path = str(output_dir / filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"\n✅ 表结构已保存到:", file=sys.stderr)
        print(f"   {output_path}", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"💡 提示:", file=sys.stderr)
        print(f"   - 文件位于项目 .aiout 目录，便于集中管理", file=sys.stderr)
        print(f"   - 如需保存到其他位置，请使用: --output <目标路径>", file=sys.stderr)
    
    except Exception as e:
        print(f"❌ 处理失败: {e}", file=sys.stderr)
        sys.exit(1)


def format_as_markdown(schema_data: Dict[str, Any]) -> str:
    """将表结构格式化为 Markdown"""
    lines = [f"# Database: {schema_data['database']}\n"]
    lines.append(f"**表数量**: {schema_data['tableCount']}\n")
    
    # 添加元数据信息
    if 'metadata' in schema_data:
        metadata = schema_data['metadata']
        lines.append("元数据信息")
        lines.append(f"- **提取时间**: {metadata.get('extractedAt', 'unknown')}")
        lines.append(f"- **数据库版本**: {metadata.get('serverVersion', 'unknown')}")
        lines.append(f"- **主机**: {metadata.get('host', 'unknown')}:{metadata.get('port', 3306)}")
        lines.append(f"- **提取器版本**: {metadata.get('extractorVersion', 'unknown')}")
        lines.append("")
    
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
