import os
import re
import csv


def process_sql_file(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"错误: 找不到文件 {input_filename}")
        return

    with open(input_filename, 'r', encoding='utf-8') as target_file:
        sql_text = target_file.read()

    # 1. 提取建表语句内部字段 (保持之前的逻辑)
    # 使用 re.DOTALL 允许跨行匹配，寻找第一个 ( 到 最后一个 ) 之间的内容
    # . 匹配除换行符外的任意字符
    # 非贪婪模式 (.*?)，迫使引擎找到第一个满足后续条件的闭合括号 )\s*; 就停止
    # 通过添加 \s*;，我们告诉正则：我们要找的是“作为语句结尾的那个括号”，而不是字段定义中的 DECIMAL(10, 2) 内部的括号
    table_match = re.search(r'CREATE TABLE.*?\((.*?)\)\s*(?:WITH.+?)?\s*;', sql_text, re.DOTALL | re.IGNORECASE)
    if not table_match:
        print("未找到有效的 CREATE TABLE 语句")
        return

    inner_content = table_match.group(1).strip()
    column_data = {}

    lines = inner_content.split('\n')
    for line in lines:
        line = line.strip().rstrip(',')
        # 排除约束行
        if not line or line.upper().startswith(('CONSTRAINT', 'PRIMARY', 'UNIQUE', 'CHECK', 'FOREIGN')):
            continue

        # 处理字段名和类型，包括 DECIMAL(10,2)
        match = re.match(r'("?\w+"?)\s+(\w+(?:\s*\([^)]+\))?)', line)
        if match:
            col_name = match.group(1).replace('"', '')
            col_type = match.group(2)
            column_data[col_name] = {'type': col_type, 'comment': ''}

    # 2. 【重点改进】提取注释，支持 schema.table.column 或 table.column
    # 逻辑：匹配最后一个点号后的内容作为列名
    comment_pattern = re.compile(
        # (?: ... ) 是非捕获分组
        # [\w".]+\. 匹配“一串字符加一个点”，末尾的 + 表示匹配一次或多次。这会吃掉 schema. 或者 schema.table.
        r"COMMENT\s+ON\s+COLUMN\s+(?:[\w\".]+\.)+([\w\"]+)\s+IS\s+'(.*?)';",
        # 不区分大小写
        re.IGNORECASE
    )

    comments = comment_pattern.findall(sql_text)

    for col_name_raw, comment_text in comments:
        # 去掉可能的双引号
        col_name = col_name_raw.replace('"', '')
        if col_name in column_data:
            column_data[col_name]['comment'] = comment_text

    # 3. 【核心增强】按字段名进行字母升序排序
    # sorted() 函数会返回一个按键排序后的列表
    sorted_columns = sorted(column_data.keys())

    # 4. 写入 CSV
    # 在保存 CSV 时使用了 encoding='utf-8-sig'。这样生成的 CSV 文件用 Excel 直接打开时，中文才不会乱码
    try:
        # Python 的 csv 模块在写入数据时，有它自己的换行处理逻辑：
        # csv.writer 内部已经根据不同系统的标准，在每一行数据末尾添加了相应的换行符（通常是 \r\n）
        # Python 的 open() 函数默认会启用“通用换行符”模式，如果你不指定 newline=''，Python 会将代码中的换行符 \n 自动转换成操作系统默认的换行符（在 Windows 上是 \r\n）
        # 如果没有 newline=''：csv 模块先写入了 \r\n，然后 Python 的 open 函数又检测到了其中的 \n，并将其再次转换成 \r\n，结果就变成了写入 \r\r\n
        # 通过设置 newline=''，你告诉 Python 的 open 函数：“不要对换行符做任何自动转换，把控制权完全交给 csv 模块。”
        with open(output_filename, 'w', encoding='utf-8-sig', newline='') as target_file:
            writer = csv.writer(target_file)
            writer.writerow(['字段名', '类型', '注释'])
            for col_name in sorted_columns:
                info = column_data[col_name]
                writer.writerow([col_name, info['type'], info['comment']])

        print(f"解析成功！已处理 {len(column_data)} 个字段，已按字母顺序保存至: {output_filename}。")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")


# --- 使用方法 ---
# 假设你有一个 input.sql 文件
# process_sql_file('input.sql', 'output.csv')

# 测试代码
if __name__ == "__main__":
    # 模拟一个复杂的 SQL 输入
    test_sql = """
        CREATE TABLE public.inventory (
            stock_id SERIAL PRIMARY KEY,
            unit_price DECIMAL(12, 2) DEFAULT 0.00,
            product_code VARCHAR(50) NOT NULL,
            available_quantity INT4,
            created_at TIMESTAMP
        );

        COMMENT ON COLUMN public.inventory.stock_id IS '库存唯一ID';
        COMMENT ON COLUMN public.inventory.unit_price IS '单价';
        COMMENT ON COLUMN public.inventory.product_code IS '产品编码';
        COMMENT ON COLUMN public.inventory.available_quantity IS '可用库存数量';
    """

    # 写入临时文件测试
    with open('test_input.sql', 'w', encoding='utf-8') as f:
        f.write(test_sql)

    process_sql_file('test_input.sql', 'inventory_dict.csv')
    process_sql_file('create_sql_test_case.sql', 'schema_output.csv')
    process_sql_file('create_sql_test_case2.sql', 'schema_output2.csv')
