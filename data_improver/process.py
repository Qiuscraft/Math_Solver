import csv
import re


def ensure_ids_in_csv(input_path, output_path):
    # 读取数据
    data = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            id_num = int(row[0])
            message = row[1]
            data[id_num] = message

    # 确保ID从0到7999都存在，缺失的补零
    for id_num in range(8000):
        if id_num not in data:
            data[id_num] = "0"

    # 按ID排序
    sorted_data = sorted(data.items())

    # 写回文件
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for id_num, message in sorted_data:
            writer.writerow([id_num, message])

def replace_message_with_last_number(input_path, output_path):
    # 定义正则表达式匹配最后一个数字
    number_pattern = re.compile(r'[-+]?\d*\.?\d+(?:/\d+)?Π?')

    # 读取数据并处理
    data = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            id_num = int(row[0])
            message = row[1]

            # 查找消息字符串中的所有数字
            numbers = number_pattern.findall(message)
            if numbers:
                # 使用最后一个数字覆盖消息字符串
                message = numbers[-1]
            else:
                # 如果没有数字，保留原消息字符串
                message = "0"

            data[id_num] = message

    # 写回文件
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for id_num, message in sorted(data.items()):
            writer.writerow([id_num, message])

if __name__ == '__main__':
    ensure_ids_in_csv('submit_ori.csv', 'merged_p1.csv')  # 确保ID从0到7999都存在
    replace_message_with_last_number('merged_p1.csv', 'merged_p2.csv')  # 提取最后一个数字作为结果
