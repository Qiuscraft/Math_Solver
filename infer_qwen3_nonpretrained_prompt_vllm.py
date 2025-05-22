import json
from typing import List

from pydantic import BaseModel
from vllm import LLM, SamplingParams
from vllm.sampling_params import GuidedDecodingParams

system_prompt_path = "./prompt/infer_qwen3_nonpretrained_prompt.txt"
test_json_path = "test.json"

with open(system_prompt_path, 'r', encoding='utf-8') as prompt_file:
    system_prompt = prompt_file.read().strip()

print("Using system prompt: \n", system_prompt)

with open(test_json_path, 'r', encoding='utf-8') as file:
    test_data = json.load(file)

print("Loaded test data from:", test_json_path, "\nTest data amount: ", len(test_data))

prompts = []
for item in test_data:
    question = item['question']
    prompt = f"{system_prompt}\n\n请你回答问题: {question}"
    prompts.append(prompt)

class MathResponse(BaseModel):
    steps: List[str]
    final_answer: str

json_schema = MathResponse.model_json_schema()

def main():
    guided_decoding_params = GuidedDecodingParams(json=json_schema)
    sampling_params = SamplingParams(temperature=0, guided_decoding=guided_decoding_params)
    llm = LLM(model="Qwen/Qwen3-0.6B", trust_remote_code=True, enable_prefix_caching=True)
    outputs = llm.generate(prompts, sampling_params)
    print("\nGenerated Outputs:\n" + "-" * 60)
    with open("submit.csv", 'w', encoding='utf-8') as submit_file:
        for question_id, output in enumerate(outputs):
            generated_text = output.outputs[0].text
            submit_file.write(f"{question_id},{generated_text!r}\n")


if __name__ == "__main__":
    main()