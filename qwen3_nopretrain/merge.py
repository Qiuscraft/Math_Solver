import csv


def merge_csv_files(output_path, *input_files):
    data = {}

    # 按优先级顺序读取文件
    for file in input_files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # 按第一个逗号分割，避免消息字符串中的逗号干扰
                id_str, message = line.split(',', 1)
                id_num = int(id_str)
                # 如果ID不存在，则添加（优先级高的文件会覆盖低优先级的）
                if id_num not in data:
                    data[id_num] = message

    # 按ID排序
    sorted_data = sorted(data.items())

    # 写入合并后的文件
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for id_num, message in sorted_data:
            writer.writerow([id_num, message])


# 使用示例
merge_csv_files('merged.csv', 'submit3.csv', 'submit2.csv', 'submit1.csv')