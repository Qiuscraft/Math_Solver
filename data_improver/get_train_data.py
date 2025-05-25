import json


def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def process(input_file, output_file, original_train_file):

    with open (input_file, 'r', encoding='utf-8') as f:
        data = read_jsonl(input_file)

    with open (original_train_file, 'r', encoding='utf-8') as f:
        original_train_file = json.load(f)

    output_data = []

    for item in data:
        question_id = item['question_id']
        for original_item in original_train_file:
            if original_item['id'] == question_id:
                question = original_item['question']
                result = dict()
                result['id'] = question
                result['question'] = question
                result['answer'] = '<think>' + item['reasoning'] + '</think>' + item['answer']
                result['instruction'] = '你需要解决数学问题，但是你只允许使用384个token。\n因此，你禁止思考，只做两步计算，每步计算禁止超过十个字。\n计算完成后，直接输出问题答案，你的输出只能是一个最终的数字，不带单位，不带任何其他计算过程。'
                output_data.append(result)
                break

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    input_file = 'correct_answers.jsonl'
    output_file = 'train.json'
    original_train_file = '../train.json'
    process(input_file, output_file, original_train_file)
