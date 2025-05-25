import json


def extract_error(error_file, ori_file, result_file):
    error_list = []
    with open(error_file, encoding="utf-8") as f:
        errors = f.readlines()
        for error_line in errors:
            error = json.loads(error_line)
            custom_id = error['custom_id']
            error_list.append(custom_id)

    result_lines = []
    with open(ori_file, encoding="utf-8") as f:
        requests = f.readlines()
        for request_line in requests:
            request = json.loads(request_line)
            custom_id = request['custom_id']
            if custom_id in error_list:
                result_lines.append(request_line)

    with open(result_file, 'w', encoding="utf-8") as f:
        f.writelines(result_lines)

if __name__ == "__main__":
    extract_error('error_202505241636.jsonl', 'batch.jsonl', 'error_batch.jsonl')