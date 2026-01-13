import os
import re
import csv


def process_sql_file(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"错误: 找不到文件 {input_filename}")
        return

    with open(input_filename, 'r', encoding='utf-8') as f:
        sql_text = f.read()

    # 1. 提取建表语句内部字段 (保持之前的逻辑)
    # 使用 re.DOTALL 允许跨行匹配，寻找第一个 ( 到 最后一个 ) 之间的内容
    # . 匹配除换行符外的任意字符
    # 非贪婪模式 (.*?)
    table_match = re.search(r'CREATE TABLE.*?\((.*)\).*?;', sql_text, re.DOTALL | re.IGNORECASE)
    if not table_match:
        return

    inner_content = table_match.group(1).strip()
    column_data = {}

    lines = inner_content.split('\n')
    for line in lines:
        line = line.strip().rstrip(',')
        if not line or line.upper().startswith(('CONSTRAINT', 'PRIMARY', 'UNIQUE', 'CHECK', 'FOREIGN', 'COMMENT ON ')):
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

    # 3. 写入 CSV
    # 在保存 CSV 时使用了 encoding='utf-8-sig'。这样生成的 CSV 文件用 Excel 直接打开时，中文才不会乱码
    with open(output_filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['字段名', '类型', '注释'])
        for col_name, info in column_data.items():
            writer.writerow([col_name, info['type'], info['comment']])

    print(f"解析成功！已处理 {len(column_data)} 个字段。")


# --- 使用方法 ---
# 假设你有一个 input.sql 文件
# process_sql_file('input.sql', 'output.csv')

# 测试代码
if __name__ == "__main__":
    # 创建一个模拟的 SQL 文件进行测试
    # test_sql = """
    #
    # """
    #
    # with open('temp_test.sql', 'w', encoding='utf-8') as f:
    #     f.write(test_sql)

    process_sql_file('create_sql_test_case.sql', 'schema_output.csv')
    process_sql_file('create_sql_test_case2.sql', 'schema_output2.csv')
