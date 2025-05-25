# -*- coding: utf-8 -*-
import json

# 读取 train.json 文件
with open("raw_train.json", "r", encoding="utf-8") as train_file:
    train_data = json.load(train_file)

# 准备写入 batch.jsonl 文件
with open("batch.jsonl", "w", encoding="utf-8") as batch_file:
    for item in train_data:
        custom_id = f"question-{item['id']}"
        question = item["question"]
        jsonl_entry = {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v4/chat/completions",
            "body": {
                "model": "glm-4-plus",
                "messages": [
                    {"role": "system", "content": "你是一个掌握python技能的小学数学老师。"},
                    {
                        "role": "user",
                        "content": f"# 任务：对输入的小学数学问题编写python程序进行解题，要求编写出来的python程序可以直接运行，运行后直接输出最终结果，最终结果必须只能是一个数字，不能带单位、不能带计算过程，数字可以是整数、小数、分数，最终结果不能带Π，如果带Π，需要代入3.14进行计算。# 问题：\"{question}\"# 输出格式：\n```python\n# 请输出python程序代码，要求你的代码可以直接运行，直接输出最终答案\n```"
                    }
                ]
            }
        }
        # 写入每行 JSONL 数据
        batch_file.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")

print("转换完成，数据已写入 batch.jsonl 文件。")