# MyBatis-Plus 配置指南 (Spring Boot 3.x)

本文档提供 Spring Boot 3.x + MyBatis-Plus + MySQL 8.x 的完整配置示例。

## Maven 依赖配置

### pom.xml

```xml
<dependencies>
    <!-- MyBatis-Plus Starter -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.9</version>
    </dependency>
    
    <!-- MySQL 8.x 驱动 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>
    
    <!-- Lombok (可选，简化代码) -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

## 数据源配置

### application.yml

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/your_database?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
    username: root
    password: your_password
    
    # HikariCP 连接池配置（Spring Boot 3.x 默认）
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 600000
      max-lifetime: 1800000
      connection-timeout: 30000

# MyBatis-Plus 配置
mybatis-plus:
  # Mapper XML 文件位置
  mapper-locations: classpath*:/mapper/**/*.xml
  
  # 实体类扫描路径
  type-aliases-package: com.your.package.entity
  
  # 全局配置
  global-config:
    db-config:
      # 主键类型（雪花算法）
      id-type: ASSIGN_ID
      
      # 表名前缀
      # table-prefix: t_
      
      # 逻辑删除字段名
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0
      
  # 配置项
  configuration:
    # 驼峰转下划线
    map-underscore-to-camel-case: true
    
    # 日志输出（开发环境）
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
    
    # 缓存配置
    cache-enabled: true
```

## MyBatis-Plus 配置类

### MybatisPlusConfig.java

```java
package com.your.package.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.BlockAttackInnerInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.OptimisticLockerInnerInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MyBatis-Plus 配置
 */
@Configuration
@MapperScan("com.your.package.mapper")
public class MybatisPlusConfig {

    /**
     * MyBatis-Plus 插件配置
     */
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        
        // 1. 分页插件
        PaginationInnerInterceptor paginationInterceptor = new PaginationInnerInterceptor(DbType.MYSQL);
        paginationInterceptor.setMaxLimit(1000L); // 单页最大限制
        paginationInterceptor.setOverflow(false); // 溢出总页数后是否进行处理
        interceptor.addInnerInterceptor(paginationInterceptor);
        
        // 2. 乐观锁插件
        interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
        
        // 3. 防止全表更新删除插件
        interceptor.addInnerInterceptor(new BlockAttackInnerInterceptor());
        
        return interceptor;
    }
}
```

## 自动填充配置

### MetaObjectHandler 实现

```java
package com.your.package.handler;

import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

/**
 * MyBatis-Plus 字段自动填充处理器
 */
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    /**
     * 插入时自动填充
     */
    @Override
    public void insertFill(MetaObject metaObject) {
        // 创建时间
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "createdAt", LocalDateTime.class, LocalDateTime.now());
        
        // 更新时间
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
        
        // 创建人（需要从上下文获取）
        // this.strictInsertFill(metaObject, "creator", String.class, getCurrentUserId());
        
        // 逻辑删除字段默认值
        this.strictInsertFill(metaObject, "deleted", Integer.class, 0);
    }

    /**
     * 更新时自动填充
     */
    @Override
    public void updateFill(MetaObject metaObject) {
        // 更新时间
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
        this.strictUpdateFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
        
        // 更新人（需要从上下文获取）
        // this.strictUpdateFill(metaObject, "updater", String.class, getCurrentUserId());
    }
}
```

## 实体类示例（DO）

### UserDO.java

```java
package com.your.package.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 用户表
 */
@Data
@TableName("user")
public class UserDO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID（雪花算法）
     */
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    /**
     * 用户名
     */
    private String username;

    /**
     * 密码
     */
    private String password;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 手机号
     */
    private String phone;

    /**
     * 状态（0-禁用 1-启用）
     */
    private Integer status;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    /**
     * 逻辑删除（0-未删除 1-已删除）
     */
    @TableLogic
    private Integer deleted;

    /**
     * 乐观锁版本号
     */
    @Version
    private Integer version;
}
```

## Mapper 接口示例

### UserMapper.java

```java
package com.your.package.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.your.package.entity.UserDO;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户 Mapper
 */
@Mapper
public interface UserMapper extends BaseMapper<UserDO> {
    // BaseMapper 已提供 CRUD 方法
    // 自定义方法可以在这里添加
}
```

## Service 层示例

### IUserService.java

```java
package com.your.package.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.your.package.entity.UserDO;

/**
 * 用户服务接口
 */
public interface IUserService extends IService<UserDO> {
    // IService 已提供常用方法
    // 自定义业务方法可以在这里添加
}
```

### UserServiceImpl.java

```java
package com.your.package.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.your.package.entity.UserDO;
import com.your.package.mapper.UserMapper;
import com.your.package.service.IUserService;
import org.springframework.stereotype.Service;

/**
 * 用户服务实现
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, UserDO> implements IUserService {
    // ServiceImpl 已实现 IService 的所有方法
    // 这里可以添加自定义业务逻辑
}
```

## 常用查询示例

### 条件查询

```java
// 1. 简单查询
UserDO user = userMapper.selectById(1L);

// 2. 条件构造器查询
QueryWrapper<UserDO> wrapper = new QueryWrapper<>();
wrapper.eq("username", "admin")
       .eq("status", 1)
       .orderByDesc("create_time");
List<UserDO> users = userMapper.selectList(wrapper);

// 3. Lambda 条件构造器（推荐，类型安全）
LambdaQueryWrapper<UserDO> lambdaWrapper = new LambdaQueryWrapper<>();
lambdaWrapper.eq(UserDO::getUsername, "admin")
             .eq(UserDO::getStatus, 1)
             .orderByDesc(UserDO::getCreateTime);
List<UserDO> users = userMapper.selectList(lambdaWrapper);

// 4. 分页查询
Page<UserDO> page = new Page<>(1, 10); // 第1页，每页10条
LambdaQueryWrapper<UserDO> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(UserDO::getStatus, 1);
Page<UserDO> result = userMapper.selectPage(page, wrapper);
List<UserDO> records = result.getRecords();
long total = result.getTotal();
```

### 批量操作

```java
// 1. 批量插入
List<UserDO> users = Arrays.asList(user1, user2, user3);
userService.saveBatch(users);

// 2. 批量更新
userService.updateBatchById(users);

// 3. 批量删除（逻辑删除）
userService.removeByIds(Arrays.asList(1L, 2L, 3L));
```

## MySQL 8.x 特性

### JSON 字段处理

```java
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;

@Data
@TableName(value = "user", autoResultMap = true)
public class UserDO {
    
    /**
     * JSON 扩展字段
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> extra;
}
```

### 时区配置

确保 MySQL 连接 URL 包含时区参数：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db?serverTimezone=Asia/Shanghai
```

### 字符集配置（支持 emoji）

```sql
-- 建表时使用 utf8mb4
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 最佳实践

### 1. 实体类命名规范

- **DO (Data Object)**: 数据库实体类，后缀 `DO`
- **DTO (Data Transfer Object)**: 数据传输对象，后缀 `DTO`
- **VO (View Object)**: 视图对象，后缀 `VO`

### 2. 字段命名规范

- 数据库: 下划线命名 (`user_name`, `create_time`)
- Java: 驼峰命名 (`userName`, `createTime`)
- MyBatis-Plus 自动处理驼峰转换

### 3. 主键策略选择

| 场景 | 推荐策略 | 说明 |
|-----|---------|------|
| 单机/主从 | AUTO | 数据库自增，简单高效 |
| 分布式 | ASSIGN_ID | 雪花算法，全局唯一 |
| UUID | ASSIGN_UUID | 字符串UUID，兼容性好 |

### 4. 逻辑删除

建议统一使用逻辑删除，避免数据丢失：

```java
@TableLogic
private Integer deleted; // 0-未删除, 1-已删除
```

### 5. 乐观锁

并发更新场景使用乐观锁：

```java
@Version
private Integer version;
```

### 6. 自动填充

统一配置创建时间、更新时间自动填充：

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

## 常见问题

### Q1: 如何处理枚举类型？

```java
import com.baomidou.mybatisplus.annotation.EnumValue;

public enum UserStatus implements IEnum<Integer> {
    DISABLED(0, "禁用"),
    ENABLED(1, "启用");

    @EnumValue
    private final int code;
    private final String desc;

    // 构造函数、getter 省略

    @Override
    public Integer getValue() {
        return this.code;
    }
}
```

### Q2: 如何自定义 SQL？

在 Mapper 接口中添加自定义方法，并在对应的 XML 文件中编写 SQL。

### Q3: 分页查询如何优化？

- 使用索引覆盖
- 避免使用 `SELECT *`
- 合理设置分页大小上限

### Q4: 如何处理多数据源？

使用 MyBatis-Plus 的 `@DS` 注解或配置动态数据源。

## 参考资源

- [MyBatis-Plus 官方文档](https://baomidou.com/)
- [Spring Boot 3.x 官方文档](https://spring.io/projects/spring-boot)
- [MySQL 8.x 官方文档](https://dev.mysql.com/doc/)
