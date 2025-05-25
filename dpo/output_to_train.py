import json

def process_output_to_train(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    train_data = []
    for item in data:
        train_item = {
            "messages": [
                {"role": "user", "content": item["question"]},
            ],
            "chosen": {
                "role": "assistant",
                "content": json.dumps(item["standard_answer"], ensure_ascii=False, indent=2)
            },
            "rejected": {
                "role": "assistant",
                "content": json.dumps(item["typical_error"], ensure_ascii=False, indent=2)
            }
        }
        train_data.append(train_item)

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for entry in train_data:
            outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')

# 使用示例
process_output_to_train('output_correct.json', 'train_correct.jsonl')