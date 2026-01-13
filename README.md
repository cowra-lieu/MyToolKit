# My ToolKit

## PG-SQL-to-CSV-Parser

一个轻量级的 Python 工具，用于解析 PostgreSQL 的 `CREATE TABLE` 语句。它能自动匹配字段定义与底部的 `COMMENT ON COLUMN` 注释，并生成 Excel 友好的 CSV 文件。

### 🌟 核心功能
- **智能解析**：支持 `DECIMAL(10,2)`、`VARCHAR(n)` 等带括号和逗号的复杂字段类型。
- **多级支持**：兼容 `schema.table.column`、`table.column` 等多种注释写法。
- **Excel 兼容**：自动处理中文乱码问题（使用 UTF-8-BOM 编码）。
- **简单易用**：无需安装第三方库，纯 Python 标准库实现。

### 🚀 快速开始

### 1. 准备 SQL 文件
将你的建表语句存入 `input.sql`：
```sql
CREATE TABLE "myschema"."orders" (
    "order_id" INT8 PRIMARY KEY,
    "total_amount" DECIMAL(12, 2),
    "user_id" INTEGER
);

COMMENT ON COLUMN "myschema"."orders"."order_id" IS '订单全局唯一标识';
COMMENT ON COLUMN myschema.orders.total_amount IS '总金额(元)';
COMMENT ON COLUMN orders.user_id IS '用户ID';
```

### 2. 运行转换脚本
```bash
python CreateSQLtoCSVParser.py
```

### 3. 查看结果

### 🛠️ 技术原理
脚本采用正则表达式提取技术：
- 使用非贪婪匹配 .*? 定位结构。
- 使用 ("?\w+"?)\s+(\w+(?:\s*\([^)]+\))?) 确保在多级 Schema 结构下准确提取列名和类型。