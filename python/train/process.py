import csv
import json
from fractions import Fraction


def get_decimal_places(fraction):
    if not '/' in str(fraction):
        return 0
    decimal_str = str(float(fraction))  # 将Fraction转换为浮点数再转为字符串
    if '.' in decimal_str:
        return len(decimal_str.split('.')[1])  # 计算小数点后的字符数
    return None


def string_refactor(input_file, output_file):
    data_dict = dict()
    id_list = []
    with open(input_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            try:
                frac = Fraction(row[1])
                if get_decimal_places(frac) == 1 or get_decimal_places(frac) == 2:
                    frac = float(frac)
            except ValueError:
                frac = Fraction(0)
            finally:
                data_id = int(row[0])
                data_dict[data_id] = str(frac)
                id_list.append(data_id)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        for data_id in id_list:
            csv_writer.writerow((data_id, data_dict[data_id]))


def get_correct_id(input_file, train_file):
    id_list = []
    with open(input_file, 'r', encoding='utf-8') as llm_answer_file:
        llm_answer_csv = csv.reader(llm_answer_file)
        with open(train_file, 'r', encoding='utf-8') as train_json_file:
            train_json = json.load(train_json_file)
            for llm_answer in llm_answer_csv:
                llm_answer_id = int(llm_answer[0])
                llm_answer_string = llm_answer[1]
                for json_item in train_json:
                    json_item_id = int(json_item['id'])
                    if json_item_id == llm_answer_id:
                        if json_item['answer'] == llm_answer_string:
                            id_list.append(llm_answer_id)
                        break
    return id_list


def extract_train_data(raw_train_json_file, output_train_json_file, id_list):
    with open(raw_train_json_file, 'r', encoding='utf-8') as raw_file:
        raw_data = json.load(raw_file)
        filtered_data = [item for item in raw_data if int(item['id']) in id_list]

    for item in filtered_data:
        del item['answer']
        del item['instruction']

    with open(output_train_json_file, 'w', encoding='utf-8') as output_file:
        json.dump(filtered_data, output_file, ensure_ascii=False, indent=4)

    return filtered_data


def insert_instruction(input_train_json_file, output_train_json_file, instruction):
    with open(input_train_json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        item['instruction'] = instruction

    with open(output_train_json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def insert_answer(input_train_json_file, output_train_json_file, glm_answer_jsonl_file):
    with open(input_train_json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    with open(glm_answer_jsonl_file, 'r', encoding='utf-8') as file:
        glm_answers = [json.loads(line) for line in file]

    for item in data:
        question_id = int(item['id'])
        for glm_answer_data in glm_answers:
            if glm_answer_data['custom_id'] == f"question-{question_id}":
                item['answer'] = glm_answer_data['response']['body']['choices'][0]['message']['content']
                break

    with open(output_train_json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    string_refactor('output.csv', 'output_p1.csv')
    print('output_p1.csv generated successfully')

    correct_id_list = get_correct_id('output_p1.csv', 'train.json')
    print('train.json generated successfully')

    filtered_data = extract_train_data('train.json', 'train_p1.json', correct_id_list)
    print(f"Extracted {len(filtered_data)} items")
    print('train_p1.json generated successfully')

    new_instruction = '# 任务：对输入的小学数学问题编写python程序进行解题，要求编写程序过程中只允许使用fractions模块进行构建数字和计算，严禁使用整型和浮点型数据，所有的数据你都要直接使用分数表示，要求编写出来的python程序可以直接运行，运行后直接输出最终结果，最终结果必须只能是一个数字，不能带单位、不能带计算过程，数字可以是整数、小数、分数，最终结果不能带Π，如果带Π，需要代入3.14进行计算。# 问题：'
    insert_instruction('train_p1.json', 'train_p2.json', new_instruction)
    print('train_p2.json generated successfully')

    insert_answer('train_p2.json', 'train_p3.json', 'output_202505251442.jsonl')
    print('train_p3.json generated successfully')
