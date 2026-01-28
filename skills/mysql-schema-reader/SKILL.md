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
- [ ] Step 3: Review and Use Output

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
# Use cache (default enabled, valid for 24 hours)
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --cache

# Set custom cache expiration (in hours)
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --cache-max-age 48

# Force refresh - ignore cache and re-extract from database
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --force-refresh
```

**Connection options**
```bash
# Set connection timeout and retry attempts
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --timeout 30 \
  --max-retries 5
```

**Note**: 
- Schema extraction results are cached by default to improve performance
- Cache is valid for 24 hours by default (configurable with `--cache-max-age`)
- Cache includes metadata: extraction time, database version, and host info
- When database schema changes, use `--force-refresh` to get the latest structure
- Cache and output files are stored in project directory (`.aiout/mysql-schema-reader/`)
- Connection failures will retry automatically (default: 3 attempts with exponential backoff)
- Use `--output` to specify a custom storage location

The output includes:
- Table names and comments
- Column names, types, nullability, keys, defaults, and comments
- Index information (name, type, uniqueness, columns)
- Foreign key relationships
- **Metadata**: Extraction timestamp, database version, host info, and extractor version

### Step 3: Review and Use Output

Present the extracted schema to the user.

**The skill only extracts database schema metadata for analysis and documentation.**

Output location:
- **Default**: Project directory (`.aiout/mysql-schema-reader/outputs/`)
- **Custom**: Use `--output` to specify a different location
- Files are named by database: `{database_name}.json` or `{database_name}.md`

Output can be used for:
1. Database design review and analysis
2. Technical documentation generation
3. Schema comparison and migration planning
4. Understanding existing database structure

## Error Handling

### Connection Failures

The script includes automatic retry with exponential backoff (default: 3 attempts).

If the connection fails after all retries:
1. **Access Denied Error**: Verify database credentials and user permissions
2. **Unknown Database Error**: Check if database name is spelled correctly
3. **Connection Refused Error**: 
   - Verify the database server is running
   - Check network connectivity and firewall settings
   - Verify host address and port
4. **Timeout Error**: 
   - Increase timeout with `--timeout 30`
   - Check network stability
5. **Host Not Allowed Error**: MySQL user permissions restrict connection source

You can customize retry behavior:
```bash
python scripts/extract_schema.py \
  --url "mysql://user:pass@host/db" \
  --max-retries 5 \
  --timeout 30
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
# Extract schema in JSON format
python scripts/extract_schema.py \
  --host localhost \
  --user root \
  --password secret123 \
  --database myapp \
  --output schema.json \
  --pretty
```

Present the extracted schema to user for review and analysis.

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

### Example 5: Force refresh with custom retry settings

**User**: "I modified some table structures in my database. The connection is slow, please extract the latest schema with more retries."

**Assistant**:
```bash
# Force refresh with extended timeout and retries
python scripts/extract_schema.py \
  --url "mysql://user:pass@localhost/mydb" \
  --force-refresh \
  --timeout 30 \
  --max-retries 5 \
  --output latest_schema.json \
  --pretty
```

This will:
- Ignore cached data and re-extract from database
- Use 30-second connection timeout
- Retry up to 5 times on connection failure
- Save output with metadata including extraction time and database version

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
3. **Documentation**: Save schema output as documentation for reference
4. **Cache Management**: Use `--force-refresh` after modifying database schema to ensure latest structure
5. **Config Files**: Use `--scan-config` to automatically detect and select configuration files in Spring Boot projects
