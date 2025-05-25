import json
import os
import sys
import csv
import tempfile
import subprocess
from fractions import Fraction
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm  # 用于进度显示

import re

def extract_code_block(code_content):
    # 使用单次匹配提取完整代码块
    pattern = r'^```python\s*(.*?)\s*```'  # 非贪婪匹配
    match = re.search(pattern, code_content, flags=re.DOTALL | re.IGNORECASE)

    if match:
        # 获取捕获组并去除首尾空白
        return match.group(1).strip()
    else:
        # 异常处理：未找到代码块的情况
        raise ValueError("No valid Python code block found")

def is_number_type(s):
    # 匹配整数
    integer_pattern = r'^[+-]?\d+$'
    # 匹配小数（包括小数点和小数部分）
    decimal_pattern = r'^[+-]?\d+\.\d+$'
    # 匹配分数（形如 a/b，a 和 b 为整数，b 不可为零）
    fraction_pattern = r'^[+-]?\d+/\d+$'

    if re.match(integer_pattern, s):
        return True
    elif re.match(decimal_pattern, s):
        return True
    elif re.match(fraction_pattern, s):
        # 检查分母是否为零
        numerator, denominator = map(int, s.lstrip('+-').split('/'))
        if denominator != 0:
            return True
    return False

def is_three_or_more_digit_decimal(s):
    """
    判断字符串是否是三位或以上的小数。

    :param s: 输入字符串
    :return: 如果是符合条件的小数，返回True；否则返回False。
    """
    # 正则表达式匹配模式：
    # ^[+-]? 表示可选的正负号
    # \d+ 表示整数部分至少有一位数字
    # \.\d{3,}$ 表示必须有小数点，且小数点后至少跟3位数字。
    pattern = r'^[+-]?\d+\.\d{3,}$'
    return bool(re.match(pattern, s))

def process_single_line(line_data):
    """处理单行数据的函数"""
    line, line_number = line_data
    try:
        data = json.loads(line.strip())
        custom_id = data['custom_id']

        # 深度提取代码片段
        code_content = data['response']['body']['choices'][0]['message']['content']

        # 使用正则表达式清理代码块标记
        code = extract_code_block(code_content)

        # 创建隔离的执行环境
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmpfile:
            tmpfile.write(code)
            tmpfile.flush()
            temp_filename = tmpfile.name

        try:
            # 使用当前Python解释器执行
            result = subprocess.run(
                [sys.executable, temp_filename],
                capture_output=True,
                text=True,
                timeout=1  # 防止无限循环
            )
            output = result.stdout or result.stderr
            output = output.strip()
            output = output.replace('\n', '\\n')
            """
            # 处理执行结果
            output = result.stdout.strip() or result.stderr.strip()
            output = output.replace('\n', ' ')  # 处理多行输出

            if is_number_type(output):
                result_number = float(output)
                if math.isclose(result_number, round(result_number), rel_tol=1e-4):
                    result_number = int(round(result_number))
                elif is_three_or_more_digit_decimal(output):
                    result_number = Fraction(result_number).limit_denominator()
                return custom_id, result_number
            else:
                # 返回原始输出文本
                return custom_id, output
            """
            return custom_id, output
        finally:
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    except Exception as e:
        return custom_id, str(e)

def process_jsonl_to_csv_parallel(input_file, output_file, max_workers=None):
    """并行处理 JSONL 文件并输出到 CSV"""

    # 1. 读取所有行并准备任务
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [(line, idx) for idx, line in enumerate(f, 1)]

    results = {}

    # 2. 使用进程池并行处理
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 使用tqdm显示进度
        futures_iterator = executor.map(process_single_line, lines)

        # 包装迭代器以显示进度条
        for custom_id, result in tqdm(futures_iterator, total=len(lines), desc="处理记录"):
            id = int(custom_id.split('-')[1])  # 提取ID

            # 所有结果都会被收集，包括错误记录
            results[id] = result

    id_list = []
    for id, _ in results.items():
        id_list.append(id)
    id_list = sorted(id_list)

    # 3. 写入CSV结果
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for id in id_list:
            writer.writerow([id, results[id]])

    return len(results)

# 使用示例
if __name__ == "__main__":
    import time
    start_time = time.time()

    input_file = "output_202505251442.jsonl"
    output_file = "output_202505251442.csv"  # 结果输出，会输出错误消息

    # 使用CPU核心数作为工作进程数
    import multiprocessing
    num_workers = max(1, multiprocessing.cpu_count())

    processed = process_jsonl_to_csv_parallel(input_file, output_file, max_workers=num_workers)

    end_time = time.time()
    print(f"处理完成! 共处理 {processed} 条记录，耗时 {end_time - start_time:.2f} 秒")