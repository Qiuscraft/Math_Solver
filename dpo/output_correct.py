import json

# 读取原始数据文件
with open('output.json', 'r', encoding='utf-8') as f:
    output_data = json.load(f)

with open('../train.json', 'r', encoding='utf-8') as f:
    train_data = json.load(f)

# 创建train数据集的ID映射字典（将字符串ID转换为整数）
train_dict = {}
for item in train_data:
    try:
        item_id = int(item['id'])
    except ValueError:
        continue  # 跳过无效的ID格式
    train_dict[item_id] = item

# 筛选符合条件的条目
selected_data = []
for output_item in output_data:
    output_id = output_item['id']

    # 检查对应ID是否存在且答案匹配
    if output_id in train_dict:
        standard_answer = output_item['standard_answer']['answer']
        train_answer = train_dict[output_id]['answer']

        if standard_answer == train_answer:
            selected_data.append(output_item)

# 写入结果文件
with open('output_correct.json', 'w', encoding='utf-8') as f:
    json.dump(selected_data, f, ensure_ascii=False, indent=2)

print(f"成功筛选出 {len(selected_data)} 条匹配数据，已保存至 output_correct.json")