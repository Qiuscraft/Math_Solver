import json
import torch
from tqdm import tqdm
from modelscope import snapshot_download, AutoTokenizer
from transformers import AutoModelForCausalLM


system_prompt_path = "prompt.txt"
test_json_new_path = "test0-999.json"

model_dir = snapshot_download("Qwen/Qwen3-0.6B", cache_dir="./", revision="master")

tokenizer = AutoTokenizer.from_pretrained("./Qwen/Qwen3-0.6B/", use_fast=False, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("./Qwen/Qwen3-0.6B/", device_map="auto", torch_dtype=torch.bfloat16)

def predict(messages, model, tokenizer):
    device = "cuda"
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    # 计算输入token数量
    input_token_count = model_inputs.input_ids.shape[1]
    print(f"输入token数量: {input_token_count}")

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    # 计算输出token数量
    output_token_count = generated_ids[0].shape[0]
    print(f"输出token数量: {output_token_count}")

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return response

with open(system_prompt_path, 'r', encoding='utf-8') as prompt_file:
    system_prompt = prompt_file.read().strip()

with open(test_json_new_path, 'r', encoding='utf-8') as file:
    test_data = json.load(file)

print("Loaded test data from:", test_json_new_path, "\nTest data amount: ", len(test_data))

with open("submit.csv", 'w', encoding='utf-8') as file:
    for idx, row in tqdm(enumerate(test_data)):
        input_value = row['question']
        id = row['id']

        print(f"正在推理: {id}: {input_value}")

        messages = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{input_value}"}
        ]
        response = predict(messages, model, tokenizer)
        response = response.replace('\n', ' ')
        file.write(f"{id},{response}\n")
        print(f"推理结果: {response}")

