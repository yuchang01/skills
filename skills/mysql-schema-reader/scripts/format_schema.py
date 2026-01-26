#!/usr/bin/env python3
"""
MySQL Schema Formatter
将提取的 MySQL 表结构转换为更适合 AI 代码生成的格式
包含 MySQL 到 Java 类型映射、注解建议等
"""

import argparse
import json
import sys
from typing import Dict, Any, List


# MySQL 到 Java 类型映射
MYSQL_TO_JAVA_TYPE_MAPPING = {
    # 整数类型
    "tinyint": "Integer",
    "smallint": "Integer",
    "mediumint": "Integer",
    "int": "Integer",
    "integer": "Integer",
    "bigint": "Long",
    
    # 浮点类型
    "float": "Float",
    "double": "Double",
    "decimal": "BigDecimal",
    "numeric": "BigDecimal",
    
    # 字符串类型
    "char": "String",
    "varchar": "String",
    "tinytext": "String",
    "text": "String",
    "mediumtext": "String",
    "longtext": "String",
    
    # 二进制类型
    "binary": "byte[]",
    "varbinary": "byte[]",
    "tinyblob": "byte[]",
    "blob": "byte[]",
    "mediumblob": "byte[]",
    "longblob": "byte[]",
    
    # 日期时间类型
    "date": "LocalDate",
    "datetime": "LocalDateTime",
    "timestamp": "LocalDateTime",
    "time": "LocalTime",
    "year": "Integer",
    
    # 其他类型
    "bit": "Boolean",
    "boolean": "Boolean",
    "json": "String",
    "enum": "String",
    "set": "String",
}


def mysql_type_to_java(mysql_type: str, column_type: str) -> Dict[str, Any]:
    """将 MySQL 类型转换为 Java 类型
    
    Args:
        mysql_type: 基础数据类型 (如 'int', 'varchar')
        column_type: 完整列类型 (如 'int(11)', 'varchar(255)')
    
    Returns:
        包含 Java 类型和相关信息的字典
    """
    # 处理 unsigned
    is_unsigned = "unsigned" in column_type.lower()
    
    # 基础类型映射
    java_type = MYSQL_TO_JAVA_TYPE_MAPPING.get(mysql_type.lower(), "String")
    
    # 特殊处理
    if mysql_type.lower() == "tinyint" and "(1)" in column_type:
        # tinyint(1) 通常表示布尔值
        java_type = "Boolean"
    
    result = {
        "javaType": java_type,
        "unsigned": is_unsigned,
        "needsImport": java_type in ["BigDecimal", "LocalDate", "LocalDateTime", "LocalTime"]
    }
    
    # 添加导入语句
    if result["needsImport"]:
        import_map = {
            "BigDecimal": "java.math.BigDecimal",
            "LocalDate": "java.time.LocalDate",
            "LocalDateTime": "java.time.LocalDateTime",
            "LocalTime": "java.time.LocalTime"
        }
        result["importStatement"] = import_map.get(java_type, "")
    
    return result


def suggest_validation_annotations(column: Dict[str, Any]) -> List[str]:
    """为字段建议验证注解"""
    annotations = []
    
    # 非空验证
    if not column["nullable"] and column["key"] != "PRI":
        annotations.append("@NotNull")
    
    # 字符串长度验证
    if column["dataType"] in ["varchar", "char"] and column["maxLength"]:
        if column["nullable"]:
            annotations.append(f'@Size(max = {column["maxLength"]})')
        else:
            annotations.append(f'@NotBlank')
            annotations.append(f'@Size(max = {column["maxLength"]})')
    
    # 邮箱验证 (根据字段名猜测)
    if "email" in column["name"].lower():
        annotations.append("@Email")
    
    # 数值范围验证
    if column["dataType"] in ["int", "integer", "bigint"] and column.get("unsigned"):
        annotations.append("@Min(0)")
    
    return annotations


def suggest_jpa_annotations(column: Dict[str, Any], table_name: str) -> List[str]:
    """为字段建议 JPA 注解"""
    annotations = []
    
    # 主键
    if column["key"] == "PRI":
        annotations.append("@Id")
        if "auto_increment" in column["extra"]:
            annotations.append("@GeneratedValue(strategy = GenerationType.IDENTITY)")
    
    # 列定义
    column_def_parts = [f'name = "{column["name"]}"']
    
    if not column["nullable"]:
        column_def_parts.append("nullable = false")
    
    if column["maxLength"]:
        column_def_parts.append(f'length = {column["maxLength"]}')
    
    if column_def_parts:
        annotations.append(f'@Column({", ".join(column_def_parts)})')
    
    # 时间戳自动更新
    if "on update CURRENT_TIMESTAMP" in column["extra"].lower():
        annotations.append("@UpdateTimestamp")
    elif "DEFAULT_GENERATED" in column["extra"] and column["dataType"] in ["datetime", "timestamp"]:
        annotations.append("@CreationTimestamp")
    
    return annotations


def suggest_mybatis_annotations(column: Dict[str, Any], table_name: str) -> List[str]:
    """为字段建议 MyBatis-Plus 注解"""
    annotations = []
    
    # 主键
    if column["key"] == "PRI":
        if "auto_increment" in column["extra"]:
            annotations.append("@TableId(type = IdType.AUTO)")
        else:
            # 雪花算法 ID （推荐用于分布式系统）
            if column["dataType"] == "bigint":
                annotations.append("@TableId(type = IdType.ASSIGN_ID)")
            elif column["dataType"] in ["varchar", "char"]:
                annotations.append("@TableId(type = IdType.ASSIGN_UUID)")
            else:
                annotations.append("@TableId")
    else:
        # 非主键字段，如果 Java 字段名与数据库列名不同，需要映射
        # 这里简化处理，实际使用时 MyBatis-Plus 会自动处理驼峰转换
        # 只有当名称不符合驼峰规则时才需要 @TableField
        pass
    
    # 自动填充（创建时间/更新时间）
    field_name_lower = column["name"].lower()
    if field_name_lower in ["create_time", "created_at", "gmt_create"]:
        if "DEFAULT_GENERATED" in column["extra"] or "CURRENT_TIMESTAMP" in str(column["default"]).upper():
            annotations.append("@TableField(fill = FieldFill.INSERT)")
    elif field_name_lower in ["update_time", "updated_at", "gmt_modified", "modify_time"]:
        if "on update CURRENT_TIMESTAMP" in column["extra"].lower():
            annotations.append("@TableField(fill = FieldFill.INSERT_UPDATE)")
        elif "DEFAULT_GENERATED" in column["extra"]:
            annotations.append("@TableField(fill = FieldFill.INSERT_UPDATE)")
    
    # 逻辑删除字段
    if field_name_lower in ["deleted", "is_deleted", "del_flag"]:
        # 默认 0=未删除, 1=已删除
        annotations.append("@TableLogic")
    
    # 乐观锁版本号
    if field_name_lower in ["version", "revision"]:
        annotations.append("@Version")
    
    return annotations


def to_camel_case(snake_str: str) -> str:
    """将下划线命名转换为驼峰命名"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_pascal_case(snake_str: str) -> str:
    """将下划线命名转换为帕斯卡命名 (首字母大写)"""
    return ''.join(x.title() for x in snake_str.split('_'))


def format_table_for_codegen(table: Dict[str, Any], orm_type: str = "jpa") -> Dict[str, Any]:
    """将表结构格式化为代码生成友好的格式
    
    Args:
        table: 表结构数据
        orm_type: ORM 框架类型 ('jpa' 或 'mybatis')
    """
    formatted_columns = []
    required_imports = set()
    
    for column in table["columns"]:
        # 类型映射
        type_info = mysql_type_to_java(column["dataType"], column["columnType"])
        
        # 字段名转换
        field_name = to_camel_case(column["name"])
        
        # 注解建议
        validation_annotations = suggest_validation_annotations(column)
        
        if orm_type == "jpa":
            orm_annotations = suggest_jpa_annotations(column, table["tableName"])
        else:  # mybatis
            orm_annotations = suggest_mybatis_annotations(column, table["tableName"])
        
        formatted_column = {
            "databaseName": column["name"],
            "javaFieldName": field_name,
            "javaType": type_info["javaType"],
            "mysqlType": column["columnType"],
            "nullable": column["nullable"],
            "isPrimaryKey": column["key"] == "PRI",
            "isAutoIncrement": "auto_increment" in column["extra"],
            "comment": column["comment"],
            "validationAnnotations": validation_annotations,
            "ormAnnotations": orm_annotations,
            "default": column["default"]
        }
        
        formatted_columns.append(formatted_column)
        
        # 收集需要导入的类
        if type_info.get("needsImport"):
            required_imports.add(type_info.get("importStatement"))
    
    # 类名建议
    class_name = to_pascal_case(table["tableName"])
    
    return {
        "tableName": table["tableName"],
        "className": class_name,
        "comment": table["comment"],
        "columns": formatted_columns,
        "requiredImports": sorted(list(required_imports)),
        "indexes": table.get("indexes", []),
        "foreignKeys": table.get("foreignKeys", [])
    }


def main():
    parser = argparse.ArgumentParser(
        description="格式化 MySQL 表结构为代码生成友好的格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从 JSON 文件读取并格式化
  python format_schema.py schema.json --orm jpa
  
  # 从标准输入读取
  python extract_schema.py --url "mysql://..." | python format_schema.py --orm mybatis
  
  # 输出到文件
  python format_schema.py schema.json --output formatted.json
        """
    )
    
    parser.add_argument('input', nargs='?', default='-', 
                       help='输入 JSON 文件路径 (默认: 标准输入)')
    parser.add_argument('--orm', choices=['jpa', 'mybatis'], default='jpa',
                       help='ORM 框架类型 (默认: jpa)')
    parser.add_argument('--output', '-o', help='输出文件路径 (默认: 标准输出)')
    parser.add_argument('--pretty', action='store_true', help='格式化 JSON 输出')
    
    args = parser.parse_args()
    
    # 读取输入
    if args.input == '-':
        schema_data = json.load(sys.stdin)
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
    
    # 格式化表结构
    formatted_tables = []
    for table in schema_data.get("tables", []):
        formatted_table = format_table_for_codegen(table, args.orm)
        formatted_tables.append(formatted_table)
    
    result = {
        "database": schema_data.get("database"),
        "ormType": args.orm,
        "tableCount": len(formatted_tables),
        "tables": formatted_tables
    }
    
    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ 格式化结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
