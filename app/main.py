from core import config
from tests import test
import time
from openai import OpenAI

SYSTEM_PROMPT_FILE = "system_prompt_default.txt"

def manual_test(user_input):
    system_prompt = config.load_system_prompt_from_file(SYSTEM_PROMPT_FILE)
    base_url, api_key, models = config.load_env_and_models()

    client = OpenAI(base_url=base_url, api_key=api_key)

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}]

    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model=models["MODEL_QWEN3_8B"],
            messages=messages,
            temperature=0.3
        )
        end_time = time.time()

        print(f"\nResponse:\n {response.choices[0].message.content}")
        print(f"\nReasoning:\n {response.choices[0].message.reasoning_content}")

        generation_time_ms = response.timings['predicted_ms']
        print(f"\n\nTime elapsed (API): {generation_time_ms:.2f} ms ({generation_time_ms / 1000:.2f} s)")
        total_time = end_time - start_time
        print(f"Time elapsed (End-to-End): {total_time:.2f} s")
    except Exception as e:
        print(f"An error occurred: {e}")

def full_test():
    #test.test_case_01()
    #test.test_case_02()
    test.test_case_03()

if __name__ == "__main__":
    #simple_test("")
    full_test()