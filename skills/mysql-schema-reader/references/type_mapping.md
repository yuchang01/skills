# MySQL 到 Java 类型映射参考

本文档提供 MySQL 数据类型到 Java 类型的映射规则，以及常用 ORM 框架的注解说明。

## 数据类型映射表

### 整数类型

| MySQL 类型 | Java 类型 | 说明 | 范围 |
|-----------|----------|------|------|
| TINYINT | Integer | 小整数 | -128 到 127 (有符号) |
| TINYINT(1) | Boolean | 布尔值 (约定俗成) | 0 或 1 |
| TINYINT UNSIGNED | Integer | 无符号小整数 | 0 到 255 |
| SMALLINT | Integer | 短整数 | -32768 到 32767 |
| MEDIUMINT | Integer | 中等整数 | -8388608 到 8388607 |
| INT / INTEGER | Integer | 标准整数 | -2147483648 到 2147483647 |
| INT UNSIGNED | Long | 无符号整数 | 0 到 4294967295 |
| BIGINT | Long | 长整数 | -2^63 到 2^63-1 |
| BIGINT UNSIGNED | BigInteger | 无符号长整数 | 0 到 2^64-1 |

### 浮点和定点类型

| MySQL 类型 | Java 类型 | 说明 | 推荐使用场景 |
|-----------|----------|------|-------------|
| FLOAT | Float | 单精度浮点 | 科学计算 (精度要求不高) |
| DOUBLE | Double | 双精度浮点 | 一般浮点计算 |
| DECIMAL(M,D) | BigDecimal | 精确定点数 | 金额、精确计算 (推荐) |
| NUMERIC(M,D) | BigDecimal | 等同于 DECIMAL | 金额、精确计算 |

**重要提示**: 涉及金额计算时，务必使用 `DECIMAL` 和 `BigDecimal`，避免浮点精度问题。

### 字符串类型

| MySQL 类型 | Java 类型 | 说明 | 最大长度 |
|-----------|----------|------|----------|
| CHAR(N) | String | 定长字符串 | 0-255 字符 |
| VARCHAR(N) | String | 变长字符串 | 0-65535 字节 |
| TINYTEXT | String | 短文本 | 255 字符 |
| TEXT | String | 普通文本 | 65535 字符 |
| MEDIUMTEXT | String | 中等文本 | 16777215 字符 |
| LONGTEXT | String | 长文本 | 4294967295 字符 |

### 二进制类型

| MySQL 类型 | Java 类型 | 说明 |
|-----------|----------|------|
| BINARY(N) | byte[] | 定长二进制 |
| VARBINARY(N) | byte[] | 变长二进制 |
| TINYBLOB | byte[] | 小二进制对象 |
| BLOB | byte[] | 普通二进制对象 |
| MEDIUMBLOB | byte[] | 中等二进制对象 |
| LONGBLOB | byte[] | 大二进制对象 |

### 日期时间类型

| MySQL 类型 | Java 类型 | 说明 | 格式示例 |
|-----------|----------|------|----------|
| DATE | LocalDate | 日期 | 2026-01-25 |
| TIME | LocalTime | 时间 | 14:30:00 |
| DATETIME | LocalDateTime | 日期时间 | 2026-01-25 14:30:00 |
| TIMESTAMP | LocalDateTime | 时间戳 | 2026-01-25 14:30:00 |
| YEAR | Integer | 年份 | 2026 |

**注意**: Java 8+ 推荐使用 `java.time` 包下的时间类型，避免使用 `java.util.Date` 和 `java.sql.Timestamp`。

### 其他类型

| MySQL 类型 | Java 类型 | 说明 |
|-----------|----------|------|
| BIT(1) | Boolean | 位类型 (单位) |
| BIT(N) | byte[] | 位类型 (多位) |
| BOOLEAN / BOOL | Boolean | 布尔值 (等同于 TINYINT(1)) |
| ENUM('a','b') | String | 枚举类型 |
| SET('a','b') | String | 集合类型 |
| JSON | String | JSON 数据 |

## JPA / Hibernate 注解

### 实体类注解

```java
@Entity
@Table(name = "table_name", 
       indexes = {@Index(name = "idx_name", columnList = "column1,column2")})
public class EntityName {
    // ...
}
```

### 字段注解

#### 主键注解

```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)  // 自增主键
private Long id;

@Id
@GeneratedValue(strategy = GenerationType.UUID)      // UUID 主键
private String id;
```

#### 列映射注解

```java
@Column(name = "column_name",                // 列名
        nullable = false,                     // 非空
        unique = true,                        // 唯一
        length = 100,                         // 长度
        precision = 10,                       // 数值精度
        scale = 2,                            // 小数位数
        columnDefinition = "TEXT")            // 自定义列定义
private String field;
```

#### 时间戳注解

```java
@CreationTimestamp                            // 创建时间自动填充
@Column(name = "created_at", updatable = false)
private LocalDateTime createdAt;

@UpdateTimestamp                              // 更新时间自动填充
@Column(name = "updated_at")
private LocalDateTime updatedAt;
```

#### 枚举注解

```java
@Enumerated(EnumType.STRING)                  // 存储枚举名称
private Status status;

@Enumerated(EnumType.ORDINAL)                 // 存储枚举序号
private Status status;
```

#### JSON 字段处理

```java
@Column(columnDefinition = "JSON")
@Convert(converter = JsonConverter.class)      // 需要自定义转换器
private Map<String, Object> metadata;
```

## MyBatis / MyBatis-Plus 注解

### 实体类注解

```java
@TableName("table_name")                       // 表名映射
@KeySequence("SEQ_USER")                       // 序列主键（Oracle/PostgreSQL）
public class EntityName {
    // ...
}
```

### 字段注解

#### 主键注解

```java
// 数据库自增主键
@TableId(type = IdType.AUTO)
private Long id;

// 雪花算法 ID（推荐用于分布式系统）
@TableId(type = IdType.ASSIGN_ID)
private Long id;

// UUID 主键
@TableId(type = IdType.ASSIGN_UUID)
private String id;

// 自定义 ID 生成器
@TableId(type = IdType.INPUT)
private Long id;
```

#### 字段映射注解

```java
@TableField("column_name")                     // 字段名映射（MyBatis-Plus 会自动处理驼峰转换）
private String fieldName;

@TableField(exist = false)                     // 非表字段
private String tempField;

@TableField(select = false)                    // 查询时不返回（敏感字段）
private String password;
```

#### 自动填充注解

```java
@TableField(fill = FieldFill.INSERT)           // 插入时填充
private LocalDateTime createTime;

@TableField(fill = FieldFill.UPDATE)           // 更新时填充
private LocalDateTime updateTime;

@TableField(fill = FieldFill.INSERT_UPDATE)    // 插入和更新时填充
private LocalDateTime modifyTime;
```

#### 逻辑删除注解

```java
@TableLogic                                     // 逻辑删除（默认 0=未删除, 1=已删除）
private Integer deleted;

@TableLogic(value = "0", delval = "1")         // 自定义逻辑删除值
private Integer isDeleted;
```

#### 版本号注解 (乐观锁)

```java
@Version                                        // 乐观锁版本号
private Integer version;
```

#### JSON 字段处理 (MyBatis-Plus)

```java
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;

@TableName(value = "user", autoResultMap = true)
public class UserDO {
    
    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> extra;           // JSON 字段
}
```

## 验证注解 (Bean Validation)

```java
import jakarta.validation.constraints.*;

@NotNull                                        // 非空
@NotBlank                                       // 非空字符串 (去除空白后)
@NotEmpty                                       // 非空集合/字符串

@Size(min = 1, max = 100)                      // 字符串/集合大小
@Length(min = 1, max = 100)                    // 字符串长度 (Hibernate)

@Min(0)                                         // 最小值
@Max(100)                                       // 最大值
@DecimalMin("0.0")                             // 小数最小值
@DecimalMax("100.0")                           // 小数最大值

@Pattern(regexp = "^[A-Za-z0-9]+$")           // 正则表达式
@Email                                          // 邮箱格式
@URL                                            // URL 格式

@Past                                           // 过去的时间
@Future                                         // 未来的时间
@PastOrPresent                                 // 过去或现在
@FutureOrPresent                               // 未来或现在
```

## 命名规范

### 数据库命名 (下划线风格)

- 表名: `user_info`, `order_detail`
- 字段名: `user_name`, `created_at`
- 索引名: `idx_user_name`, `uk_email`
- 外键名: `fk_order_user_id`

### Java 命名 (驼峰风格)

- 类名: `UserInfo`, `OrderDetail` (帕斯卡命名)
- 字段名: `userName`, `createdAt` (驼峰命名)
- 方法名: `getUserName()`, `setCreatedAt()` (驼峰命名)

### 转换规则

| 数据库命名 | Java 命名 |
|-----------|----------|
| user_id | userId |
| created_at | createdAt |
| is_deleted | isDeleted / deleted |
| order_detail | OrderDetail (类名) |

## 最佳实践

### 1. 主键选择

- **自增 ID**: 适合单机或主从架构，简单高效
- **UUID**: 全局唯一，但索引性能较差
- **雪花算法**: 兼顾唯一性和索引性能，推荐分布式场景

### 2. 时间字段

```java
// 推荐使用 LocalDateTime (Java 8+)
private LocalDateTime createdAt;

// 避免使用 Date 和 Timestamp
// private Date createdAt;  // 不推荐
```

### 3. 金额字段

```sql
-- 数据库
DECIMAL(10, 2)  -- 总共10位，小数点后2位
```

```java
// Java
private BigDecimal amount;
```

### 4. 布尔字段

```sql
-- 数据库
TINYINT(1) DEFAULT 0
```

```java
// Java
private Boolean isActive;  // 或 private boolean isActive;
```

### 5. 枚举字段

```sql
-- 数据库 (推荐使用 VARCHAR 存储枚举名称)
VARCHAR(20) DEFAULT 'ACTIVE'
```

```java
// Java
public enum Status {
    ACTIVE, INACTIVE, PENDING
}

@Enumerated(EnumType.STRING)  // 存储名称，便于阅读和维护
private Status status;
```

### 6. JSON 字段

```sql
-- 数据库
JSON
```

```java
// Java (需要自定义转换器)
@Column(columnDefinition = "JSON")
@Convert(converter = JacksonJsonConverter.class)
private Map<String, Object> attributes;
```

## 常见问题

### Q1: TIMESTAMP 和 DATETIME 的区别？

- **TIMESTAMP**: 存储 UTC 时间，范围 1970-2038，受时区影响
- **DATETIME**: 存储实际时间，范围 1000-9999，不受时区影响

**推荐**: 业务时间使用 `DATETIME`，记录时间使用 `TIMESTAMP`

### Q2: INT UNSIGNED 应该映射为什么类型？

INT UNSIGNED 的最大值超过 Java Integer 的最大值，建议映射为 `Long`。

### Q3: 如何处理 TINYINT(1)？

MySQL 中 `TINYINT(1)` 约定俗成表示布尔值，应映射为 `Boolean`。

### Q4: 字符编码问题？

确保数据库、表、字段都使用 `utf8mb4` 编码，支持完整的 Unicode 字符 (包括 emoji)。

```sql
CREATE TABLE user (
    id INT PRIMARY KEY,
    name VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## MySQL 8.x 特性

### 1. 新增数据类型

#### JSON 字段

MySQL 8.x 原生支持 JSON 类型：

```sql
-- 数据库定义
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    extra JSON
);

-- 插入数据
INSERT INTO user (id, extra) VALUES 
(1, '{"age": 30, "city": "Beijing"}');

-- 查询 JSON 字段
SELECT extra->>'$.age' AS age FROM user WHERE id = 1;
```

**Java 处理**：

```java
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.fasterxml.jackson.core.type.TypeReference;

@Data
@TableName(value = "user", autoResultMap = true)
public class UserDO {
    
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    // 方式 1: 使用 Map
    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> extra;
    
    // 方式 2: 使用自定义类
    @TableField(typeHandler = JacksonTypeHandler.class)
    private UserExtra extra;
}

// 自定义 Extra 类
@Data
public class UserExtra {
    private Integer age;
    private String city;
}
```

### 2. 窗口函数 (Window Functions)

MySQL 8.x 支持窗口函数，用于复杂的分析查询：

```sql
-- 排名
SELECT 
    name,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS rank
FROM student;

-- 分组排名
SELECT 
    department,
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employee;
```

### 3. CTE (公用表表达式)

```sql
-- 递归查询组织架构
WITH RECURSIVE org_tree AS (
    SELECT id, name, parent_id, 1 AS level
    FROM organization
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT o.id, o.name, o.parent_id, ot.level + 1
    FROM organization o
    INNER JOIN org_tree ot ON o.parent_id = ot.id
)
SELECT * FROM org_tree;
```

### 4. 原子 DDL (Atomic DDL)

MySQL 8.x 中的 DDL 操作是原子性的，失败会自动回滚。

### 5. 隐藏列 (Invisible Columns)

```sql
-- 创建隐藏列
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50),
    password VARCHAR(100) INVISIBLE  -- 隐藏列
);

-- SELECT * 不会返回隐藏列
SELECT * FROM user;  -- 只返回 id, name

-- 显式查询需要指定列名
SELECT id, name, password FROM user;
```

**Java 处理**：

```java
@Data
@TableName("user")
public class UserDO {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    private String name;
    
    @TableField(select = false)  // MyBatis-Plus 中不查询
    private String password;
}
```

### 6. 字符集优化

MySQL 8.x 默认字符集为 `utf8mb4`，支持 emoji 和完整 Unicode。

```sql
-- 建表时指定字符集
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    bio TEXT
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;
```

**连接字符串配置**：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db?useUnicode=true&characterEncoding=utf8mb4&serverTimezone=Asia/Shanghai
```

### 7. 角色和权限管理

MySQL 8.x 引入了角色 (Roles) 管理：

```sql
-- 创建角色
CREATE ROLE 'app_developer';

-- 赋予权限
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'app_developer';

-- 将角色分配给用户
GRANT 'app_developer' TO 'dev_user'@'localhost';
```

### 8. 性能优化

#### 不可见索引 (Invisible Indexes)

```sql
-- 创建不可见索引（用于测试）
CREATE INDEX idx_name ON user(name) INVISIBLE;

-- 使索引可见
ALTER TABLE user ALTER INDEX idx_name VISIBLE;
```

#### 降序索引

```sql
-- 创建降序索引
CREATE INDEX idx_create_time ON user(create_time DESC);
```

### 9. 时区支持

MySQL 8.x 原生支持时区转换：

```sql
-- 使用 TIMESTAMP 类型，自动处理时区
CREATE TABLE event (
    id BIGINT PRIMARY KEY,
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Java 配置**：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db?serverTimezone=Asia/Shanghai
```

```java
// 使用 LocalDateTime，Spring Boot 自动处理时区
@Data
public class EventDO {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime eventTime;
}
```

### 10. MySQL 8.x 最佳实践

#### 连接配置

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver  # MySQL 8.x 驱动
    url: jdbc:mysql://localhost:3306/db?
      useUnicode=true&
      characterEncoding=utf8mb4&
      serverTimezone=Asia/Shanghai&
      useSSL=false&
      allowPublicKeyRetrieval=true&
      rewriteBatchedStatements=true  # 批量操作优化
```

#### 建表规范

```sql
CREATE TABLE user (
    id BIGINT PRIMARY KEY COMMENT '主键 ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted TINYINT(1) DEFAULT 0 COMMENT '逻辑删除',
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_create_time (create_time DESC)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='用户表';
```

#### 性能优化提示

1. **使用合适的索引**：为常用查询字段创建索引
2. **避免 SELECT ***：显式指定需要的列
3. **使用连接池**：HikariCP 是 Spring Boot 3.x 默认连接池
4. **批量操作优化**：启用 `rewriteBatchedStatements=true`
5. **合理使用事务**：避免长事务，合理控制事务粒度

---

## 参考资源

- [MySQL 8.x 官方文档](https://dev.mysql.com/doc/refman/8.0/en/)
- [MyBatis-Plus 官方文档](https://baomidou.com/)
- [Spring Boot 3.x 官方文档](https://spring.io/projects/spring-boot)
- [Java Bean Validation 规范](https://beanvalidation.org/)

---

**更新日期**: 2026-01-25  
**适用版本**: MySQL 8.x + MyBatis-Plus 3.5.x + Spring Boot 3.x
