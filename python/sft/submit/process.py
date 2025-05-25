import csv
import os
import re
import subprocess
import sys
import tempfile


def extract_code_block(code_content):
    pattern = r'^```python\s*(.*?)\s*```'  # 非贪婪匹配
    match = re.search(pattern, code_content, flags=re.DOTALL | re.IGNORECASE)

    if match:
        lines = match.group(1).split('\\n')
        return '\n'.join(line for line in lines if line)
    else:
        raise ValueError("No valid Python code block found")


def get_python_output(llm_answer):
    try:
        code = extract_code_block(llm_answer)

        # 创建隔离的执行环境
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmpfile:
            tmpfile.write(code)
            tmpfile.flush()
            temp_filename = tmpfile.name

        # 使用当前Python解释器执行
        result = subprocess.run(
            [sys.executable, temp_filename],
            capture_output=True,
            text=True,
            timeout=1,  # 防止无限循环
            encoding='utf-8'  # 显式指定编码为 utf-8
        )

        # 清理临时文件
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

        output = result.stdout or result.stderr
        if output is None:
            output = 'None'
        output = output.strip()
        output = output.replace('\n', '\\n')
        return output

    except ValueError as e:
        return str(e)


def generate_answer_csv(input_file, output_file):
    data = dict()
    with open(input_file, 'r', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile)
        for row in csv_reader:
            row_id = int(row[0])
            row_result = str(get_python_output(row[1]))
            data[row_id] = row_result

    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        for row_id, row_result in sorted(data.items()):
            csv_writer.writerow([row_id, row_result])


if __name__ == '__main__':
    ifile = 'output'
    generate_answer_csv(f"{ifile}.csv", f"{ifile}_p1.csv")

