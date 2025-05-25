import json

def convert_train_to_batch(train_json_path, batch_jsonl_path):
    """
    将train.json中的问题转换为example.jsonl格式并写入batch.jsonl文件

    Args:
        train_json_path: 训练数据JSON文件的路径
        batch_jsonl_path: 输出的batch.jsonl文件路径
    """
    try:
        # 读取训练数据
        with open(train_json_path, 'r', encoding='utf-8') as f:
            train_data = json.load(f)

        # 定义格式化模板部分（包含反斜杠的部分）
        format_template = '\\\"推理步骤\\\": \\\" \\\", \\\"最终答案\\\": \\\" \\\" }'

        # 写入batch.jsonl文件
        with open(batch_jsonl_path, 'w', encoding='utf-8') as f:
            for i, item in enumerate(train_data):
                # 获取问题ID和内容
                question_id = item['id']
                question_content = item['question']

                # 创建完整的用户内容
                user_content = f"#任务：推理解决以下这个小学数学问题，并按照指定的格式输出结果。问题：{question_content}。# 输出格式说明：你需要在推理步骤中仅用数学语言描述解题过程，在最终答案中直接写出最后的一个数字答案，不要带单位，不要带其他任何计算过程。# 输出格式：'''{format_template} '''"

                # 创建模板
                template = {
                    "custom_id": f"math_solver_{question_id}",
                    "method": "POST",
                    "url": "/v4/chat/completions",
                    "body": {
                        "model": "glm-4",
                        "messages": [
                            {"role": "system", "content": "你是一个小学数学专家。"},
                            {"role": "user", "content": user_content}
                        ]
                    }
                }

                # 写入JSONL文件（每行一个JSON对象）
                f.write(json.dumps(template, ensure_ascii=False) + '\n')

        print(f"成功将 {len(train_data)} 条记录转换并写入 {batch_jsonl_path}")

    except Exception as e:
        print(f"转换过程中出错: {e}")

# 示例使用
if __name__ == "__main__":
    convert_train_to_batch("train.json", "batch.jsonl")