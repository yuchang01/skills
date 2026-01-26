---
name: mysql-schema-reader
description: Extract and format MySQL database table schema (metadata) for analysis and documentation. This skill ONLY reads and formats database structure - does not generate any code. Use when users need to read database table structures, perform reverse engineering from databases, analyze database design, or export schema documentation. Triggers include "read MySQL schema", "extract table structure", "database reverse engineering", "get table metadata", "analyze database design".
---

# MySQL Schema Reader

Extract MySQL database table structures and convert them into structured formats for analysis and documentation. This skill provides metadata about tables, columns, indexes, and foreign keys without accessing actual data.

**Note: This skill only extracts and formats schema information. It does not generate any code.**

## Workflow

Copy this checklist to track progress:
- [ ] Step 1: Connect to MySQL Database
- [ ] Step 2: Extract Table Schema
- [ ] Step 3: (Optional) Format for Code Generation
- [ ] Step 4: Review and Use Output

### Step 1: Connect to MySQL Database

Gather database connection information from the user:
- Host address
- Port (default: 3306)
- Username
- Password
- Database name
- Table names (optional, extract all tables if not specified)

**Security Note**: Never log passwords or save them to files. Connection credentials should only be used during script execution.

### Step 2: Extract Table Schema

Use `scripts/extract_schema.py` to extract table metadata.

**Option A: Scan and select configuration file (Recommended)**
```bash
python scripts/extract_schema.py --scan-config /path/to/project
```
This will:
- Scan `src/main/resources/application-local.yaml/yml` and `src/test/resources/application-local.yaml/yml`
- Display all found configuration files
- Prompt you to select one if multiple files are found
- Automatically extract database connection info from the selected file

**Option B: Using connection string**
```bash
python scripts/extract_schema.py --url "mysql://user:password@localhost:3306/database_name"
```

**Option C: Using individual parameters**
```bash
python scripts/extract_schema.py \
  --host localhost \
  --port 3306 \
  --user root \
  --password your_password \
  --database mydb
```

**Extract specific tables only**
```bash
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --tables users orders products
```

**Output to file**
```bash
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --output schema.json \
  --pretty
```

**Markdown format output**
```bash
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --format markdown \
  --output schema.md
```

**Cache and force refresh**
```bash
# Use cache (default enabled)
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --cache

# Force refresh - ignore cache and re-extract from database
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --force-refresh
```

**Note**: 
- Schema extraction results are cached by default to improve performance
- When database schema changes, use `--force-refresh` to get the latest structure
- Cache files are stored in `~/.mysql_schema_cache/`
- Use `--no-cache` to completely disable caching

The output includes:
- Table names and comments
- Column names, types, nullability, keys, defaults, and comments
- Index information (name, type, uniqueness, columns)
- Foreign key relationships

### Step 3: (Optional) Format for Code Generation

Use `scripts/format_schema.py` to convert raw schema into code-generation-friendly format with:
- MySQL to Java type mappings
- Suggested ORM annotations (JPA or MyBatis-Plus)
- Validation annotation suggestions
- Camel case field name conversions
- Required import statements

**Format for JPA/Hibernate**
```bash
python scripts/format_schema.py schema.json --orm jpa --pretty
```

**Format for MyBatis/MyBatis-Plus**
```bash
python scripts/format_schema.py schema.json --orm mybatis --pretty
```

**Pipeline: Extract and format in one command**
```bash
python scripts/extract_schema.py --url "mysql://user:pass@host/db" | \
python scripts/format_schema.py --orm jpa --output formatted.json --pretty
```

The formatted output includes:
- Java class name suggestions (PascalCase)
- Java field names (camelCase)
- Java type mappings
- JPA/MyBatis annotations
- Validation annotations (@NotNull, @Size, @Email, etc.)
- Required import statements

### Step 4: Review and Use Output

Present the extracted or formatted schema to the user.

**The skill only extracts and formats database schema metadata.**

Output can be:
1. Directly shown in the conversation for review
2. Saved to a file for documentation
3. Used for database analysis and design review

The formatted schema includes:
- Table and column metadata
- Type mappings (MySQL → Java)
- Suggested annotations (JPA/MyBatis-Plus)
- Validation annotations
- Import statements

## Type Mapping Reference

For detailed MySQL to Java type mappings, ORM annotations, and best practices, see [references/type_mapping.md](references/type_mapping.md).

For complete MyBatis-Plus configuration guide (Spring Boot 3.x + MySQL 8.x), see [references/mybatis-plus-config.md](references/mybatis-plus-config.md).

Key mappings:
- `INT` → `Integer`, `BIGINT` → `Long`
- `VARCHAR/TEXT` → `String`
- `DECIMAL` → `BigDecimal` (for monetary values)
- `DATETIME/TIMESTAMP` → `LocalDateTime`
- `DATE` → `LocalDate`
- `TINYINT(1)` → `Boolean`

## Error Handling

### Connection Failures

If the connection fails:
1. Verify database credentials
2. Check if the database server is running
3. Verify network connectivity and firewall settings
4. Ensure the MySQL Python driver is installed:
   ```bash
   pip install mysql-connector-python
   # or
   pip install pymysql
   ```

### Table Not Found

If specified tables don't exist:
- The script will list available tables
- Verify table names are spelled correctly
- Check if the user has permissions to access the tables

### Missing Dependencies

If import errors occur:
```bash
# Install required packages
pip install mysql-connector-python pyyaml
```

## Usage Examples

### Example 1: Scan configuration and extract tables

**User**: "Scan my Spring Boot project at D:\projects\myapp and extract the database schema."

**Assistant**:
```bash
# Scan and select config file
python scripts/extract_schema.py --scan-config D:\projects\myapp
```

The tool will list all found `application-local.yaml/yml` files and prompt for selection. After selection, it will automatically extract database connection info and table schemas.

### Example 2: Extract all tables for analysis

**User**: "Read the schema from my MySQL database at localhost, database name is 'myapp', user 'root', password 'secret123'."

**Assistant**:
```bash
# Extract schema
python scripts/extract_schema.py \
  --host localhost \
  --user root \
  --password secret123 \
  --database myapp \
  --output raw_schema.json \
  --pretty

# Format for MyBatis-Plus
python scripts/format_schema.py raw_schema.json \
  --orm mybatis \
  --output mybatis_schema.json \
  --pretty
```

Present the formatted schema to user for review and analysis.

### Example 3: Extract specific tables only

**User**: "I only need the 'users' and 'orders' tables from mysql://dev:password@db.example.com:3306/ecommerce"

**Assistant**:
```bash
python scripts/extract_schema.py \
  --url "mysql://dev:password@db.example.com:3306/ecommerce" \
  --tables users orders \
  --format markdown \
  --output tables.md
```

### Example 4: Quick extraction for documentation

**User**: "Generate markdown documentation for all tables in the 'inventory' database."

**Assistant**:
```bash
python scripts/extract_schema.py \
  --url "mysql://user:pass@localhost/inventory" \
  --format markdown \
  --output inventory_schema.md
```

### Example 5: Force refresh after schema changes

**User**: "I modified some table structures in my database. Please extract the latest schema."

**Assistant**:
```bash
# Force refresh to get latest schema
python scripts/extract_schema.py \
  --url "mysql://user:pass@localhost/mydb" \
  --force-refresh \
  --output latest_schema.json \
  --pretty
```

This will ignore cached data and re-extract the current table structure from the database.

## Limitations

- This skill **only reads and formats table metadata** - does not generate any code
- Does not access actual table data, only schema information
- Does not support stored procedures, triggers, or views
- Does not support database-specific features beyond basic table structure
- Connection credentials are required (ensure secure handling)
- Schema results are cached by default; use `--force-refresh` when database schema changes

## Best Practices

1. **Security**: Never commit database credentials to version control
2. **Performance**: Extract only needed tables for large databases
3. **Validation**: Review extracted schema before code generation
4. **Documentation**: Save schema output as documentation for reference
5. **Type Mapping**: Consult [references/type_mapping.md](references/type_mapping.md) for accurate type conversions
6. **Cache Management**: Use `--force-refresh` after modifying database schema to ensure latest structure
7. **Config Files**: Use `--scan-config` to automatically detect and select configuration files in Spring Boot projects
