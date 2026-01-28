# 技术主题分类体系

本文档定义了AI交互记录的标准化分类体系，用于组织和检索技术对话。

## 一级分类：技术栈

### 编程语言
- `java` - Java语言及生态
- `python` - Python语言及生态
- `javascript` - JavaScript/TypeScript
- `go` - Go语言
- `rust` - Rust语言
- `cpp` - C/C++

### Java生态框架
- `spring` - Spring Framework
- `spring-boot` - Spring Boot
- `spring-cloud` - Spring Cloud微服务
- `spring-statemachine` - Spring状态机
- `mybatis` - MyBatis ORM
- `hibernate` - Hibernate ORM
- `netty` - Netty网络框架
- `dubbo` - Apache Dubbo

### 中间件
- `redis` - Redis缓存
- `kafka` - Apache Kafka消息队列
- `rabbitmq` - RabbitMQ消息队列
- `elasticsearch` - Elasticsearch搜索引擎
- `zookeeper` - ZooKeeper协调服务
- `nacos` - Nacos配置中心

### 数据库
- `mysql` - MySQL数据库
- `postgresql` - PostgreSQL
- `mongodb` - MongoDB
- `oracle` - Oracle数据库

### 前端技术
- `react` - React框架
- `vue` - Vue.js框架
- `angular` - Angular框架
- `webpack` - Webpack构建工具
- `vite` - Vite构建工具

### 工具与平台
- `git` - Git版本控制
- `docker` - Docker容器
- `kubernetes` - Kubernetes容器编排
- `jenkins` - Jenkins CI/CD
- `maven` - Maven构建工具
- `gradle` - Gradle构建工具

## 二级分类：知识领域

### 基础概念 (concept)
理论知识、术语定义、工作原理
- 技术原理解释
- 概念辨析
- 架构设计思想

### 配置使用 (configuration)
环境搭建、参数配置、基本用法
- 安装部署
- 配置文件
- 快速开始

### 实现细节 (implementation)
API使用、代码实现、最佳实践
- API调用
- 代码示例
- 设计模式

### 问题诊断 (troubleshooting)
错误排查、性能调优、调试技巧
- Bug排查
- 性能问题
- 异常处理

### 架构设计 (architecture)
系统架构、扩展性、可维护性
- 系统设计
- 架构演进
- 技术选型

### 对比分析 (comparison)
方案选型、技术对比、优劣分析
- 技术对比
- 方案选择
- 权衡分析

## 三级分类：具体知识点

### Spring State Machine 示例

```
spring-statemachine/
├── concept/              # 基础概念
│   ├── state            # 状态定义
│   ├── event            # 事件触发
│   ├── transition       # 转换规则
│   └── context          # 上下文对象
├── configuration/        # 配置使用
│   ├── dependencies     # 依赖配置
│   ├── state-config     # 状态配置
│   └── builder-pattern  # Builder模式
├── implementation/       # 实现细节
│   ├── guard            # Guard条件
│   ├── action           # Action动作
│   ├── listener         # 事件监听
│   └── persistence      # 状态持久化
├── troubleshooting/      # 问题诊断
│   ├── state-not-change # 状态不转换
│   ├── event-lost       # 事件丢失
│   └── performance      # 性能问题
└── architecture/         # 架构设计
    ├── order-flow       # 订单流程设计
    ├── approval-flow    # 审批流程设计
    └── multi-statemachine # 多状态机管理
```

### Redis 示例

```
redis/
├── concept/
│   ├── data-structure   # 数据结构
│   ├── persistence      # 持久化机制
│   └── replication      # 主从复制
├── configuration/
│   ├── installation     # 安装部署
│   ├── redis-conf       # 配置文件
│   └── cluster-setup    # 集群搭建
├── implementation/
│   ├── string-ops       # 字符串操作
│   ├── hash-ops         # 哈希操作
│   ├── list-ops         # 列表操作
│   ├── cache-pattern    # 缓存模式
│   └── distributed-lock # 分布式锁
├── troubleshooting/
│   ├── cache-penetration # 缓存穿透
│   ├── cache-avalanche   # 缓存雪崩
│   ├── hotkey-issue      # 热key问题
│   └── memory-issue      # 内存问题
└── architecture/
    ├── cache-strategy    # 缓存策略
    ├── high-availability # 高可用设计
    └── performance-tuning # 性能优化
```

### MyBatis 示例

```
mybatis/
├── concept/
│   ├── orm-mapping      # ORM映射概念
│   ├── sql-session      # SqlSession
│   └── mapper-proxy     # Mapper代理
├── configuration/
│   ├── mybatis-config   # 配置文件
│   ├── mapper-xml       # Mapper XML
│   └── annotation-config # 注解配置
├── implementation/
│   ├── crud-operations  # CRUD操作
│   ├── dynamic-sql      # 动态SQL
│   ├── result-mapping   # 结果映射
│   └── association      # 关联查询
├── troubleshooting/
│   ├── lazy-loading     # 懒加载问题
│   ├── n-plus-1         # N+1查询
│   └── cache-issue      # 缓存问题
└── architecture/
    ├── plugin-develop   # 插件开发
    ├── batch-processing # 批量处理
    └── multi-datasource # 多数据源
```

## 标签规范

### 命名规则

**技术栈标签：**
- 格式：小写+连字符
- 示例：`spring-statemachine`, `redis-cluster`
- 保持与官方命名一致

**知识点标签：**
- 中文：描述性强，易于理解
- 英文：技术术语、API名称
- 示例：`Guard条件`, `externalTransition`, `缓存穿透`

**场景标签：**
- 业务场景：`订单流程`, `支付场景`, `用户认证`
- 技术场景：`高并发`, `分布式`, `微服务`

### 标签层级

**一级标签（必填）：**
- 技术栈：如`spring-statemachine`
- 领域：如`状态机`, `缓存`, `ORM`

**二级标签（必填）：**
- 知识领域：如`implementation`, `troubleshooting`

**三级标签（建议）：**
- 具体知识点：如`Guard条件`, `缓存穿透`

**场景标签（可选）：**
- 应用场景：如`订单流程`, `高并发`

### 标签组合示例

**示例1：Spring状态机Guard条件**
```yaml
topic: spring-statemachine
domain: 状态机
category: implementation
tags:
  - Guard条件
  - 条件判断
  - 最佳实践
  - 订单流程
```

**示例2：Redis缓存穿透问题**
```yaml
topic: redis
domain: 缓存
category: troubleshooting
tags:
  - 缓存穿透
  - 布隆过滤器
  - 空值缓存
  - 高并发
```

## 目录组织结构

### 按主题分类

```
records/
└── by-topic/
    ├── spring-statemachine/
    │   ├── concept/
    │   ├── implementation/
    │   └── troubleshooting/
    ├── redis/
    │   ├── concept/
    │   ├── implementation/
    │   └── troubleshooting/
    └── mybatis/
        ├── concept/
        ├── implementation/
        └── troubleshooting/
```

### 按知识点分类

```
records/
└── by-concept/
    ├── guard-condition/           # Guard条件相关
    │   ├── spring-statemachine/
    │   └── workflow-engine/
    ├── cache-penetration/         # 缓存穿透相关
    │   ├── redis/
    │   └── memcached/
    └── dynamic-sql/               # 动态SQL相关
        ├── mybatis/
        └── hibernate/
```

### 文件命名规范

**格式：**
```
[主题]-[简短描述]-[日期时间].md
```

**示例：**
```
spring-statemachine-guard-condition-20260127-143022.md
redis-cache-penetration-solution-20260127-150530.md
mybatis-dynamic-sql-usage-20260127-163045.md
```

**命名规则：**
- 全部小写
- 使用连字符分隔
- 日期格式：YYYYMMDD
- 时间格式：HHMMSS（24小时制）

## 索引文件结构

### 主索引 (index.md)

```markdown
# AI交互记录索引

## 统计概览
- 总记录数：128
- 技术栈数：15
- 知识点数：87
- 最近更新：2026-01-27

## 按技术栈分类

### Spring State Machine (23条)
- [基础概念] 15条
- [实现细节] 6条  
- [问题排查] 2条

### Redis (18条)
- [基础概念] 8条
- [实现细节] 7条
- [问题排查] 3条

## 最近记录
1. [Spring状态机 - Guard条件使用](records/...) - 2026-01-27
2. [Redis - 缓存穿透解决方案](records/...) - 2026-01-26
...

## 热门标签
1. Guard条件 (12次)
2. 缓存策略 (10次)
3. 动态SQL (8次)
...
```

### 技术栈索引

```markdown
# Spring State Machine 对话索引

## 概览
- 记录数：23
- 首次记录：2026-01-10
- 最近更新：2026-01-27

## 按知识领域分类

### 基础概念 (15条)
- [状态机原理](link) - 2026-01-10
- [状态和事件](link) - 2026-01-12
...

### 实现细节 (6条)
- [Guard条件使用](link) - 2026-01-27
- [Action动作详解](link) - 2026-01-20
...

## 知识点覆盖
- ✅ 状态定义
- ✅ 事件触发
- ✅ Guard条件
- ⬜ 状态持久化（待学习）
- ⬜ 集群部署（待学习）
```

## 扩展性设计

### 新增技术栈

添加新技术栈时需要：
1. 在一级分类中注册技术名称
2. 创建对应的目录结构
3. 定义该技术的三级知识点分类
4. 更新索引文件

### 自定义分类

支持用户自定义：
- 个人习惯的标签名称
- 特定项目的分类维度
- 自定义的知识点层级

### 迁移和导出

支持：
- 按主题导出完整记录
- 生成学习报告
- 迁移到其他知识管理工具
