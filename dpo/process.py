import json
import re

def process_data(total_output_path: str, train_path: str, output_path: str):
    with open(train_path, 'r', encoding='utf-8') as train_file:
        train_data = json.load(train_file)
    question_map = {item['id']: item['question'] for item in train_data}

    result = []

    with open(total_output_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)

            # 提取ID（处理不同格式的ID字段）
            custom_id = data.get('custom_id', '')
            problem_id = custom_id.split('_')[-1]

            question = question_map.get(problem_id)

            # 提取响应内容
            content = data['response']['body']['choices'][0]['message']['content']

            print("==========\n", content)

            while True:
                old_content = content

                lines = content.split('\n')
                while lines and any('\u4e00' <= char <= '\u9fff' for char in lines[-1]):
                    lines.pop()
                content = '\n'.join(lines)

                while content.endswith('\n') or content.endswith(' '):
                    content = content[:-1]

                while content.endswith('`') and not content.endswith('\n```'):
                    content = content[:-1]

                while not content.endswith('\n```') and not content.endswith(']') and not content.endswith('}'):
                    content = content[:-1]

                if content.endswith('}'):
                    content = ']' + content[1:]

                # 处理内容，去除多余的反引号
                while content.startswith('`') and not content.startswith('```json\n'):
                    content = content[1:]

                while content.startswith(' '):
                    content = content[1:]

                if content.startswith('{'):
                    content = '[' + content[1:]

                if old_content == content:
                    break

            if not content.startswith('```json\n'):
                content = '```json\n' + content
            if not content.endswith('\n```'):
                content = content + '\n```'

            # 使用正则表达式提取JSON部分
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)

            if not json_match:
                print('not json_match: \n', content)
                return

            raw_json = json_match.group(1)

            try:
                # 尝试解析 JSON 数据
                answers = json.loads(raw_json)
                if not isinstance(answers, list):
                    raise ValueError(f"Extracted JSON is not a list: {answers}")
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}. Raw JSON:\n{raw_json}")
                continue
            except ValueError as e:
                print(f"ValueError: {e}. Raw JSON:\n{raw_json}")
                continue

            # 构建标准答案和典型错误
            standard = next((a for a in answers if a['类型'] == '标准答案'), {})
            error = next((a for a in answers if a['类型'] == '典型错误'), {})

            # 构建最终结果项
            result_item = {
                "id": int(problem_id),
                "question": question,
                "standard_answer": {
                    "steps": standard.get('解题步骤', ''),
                    "answer": standard.get('最终答案', '')
                },
                "typical_error": {
                    "steps": error.get('解题步骤', ''),
                    "answer": error.get('最终答案', '')
                }
            }
            result.append(result_item)

    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# 使用示例
process_data(
    total_output_path='total_output.jsonl',
    train_path='../train.json',
    output_path='output.json'
)



