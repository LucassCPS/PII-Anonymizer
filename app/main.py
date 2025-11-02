from tests import test
from core.config import ModelEnum, load_model, load_api_key, load_base_url
from utils import prompts
from utils import report_printer
from openai import OpenAI
from pathlib import Path
import sys

MODEL = load_model(ModelEnum.GEMMA3_QAT_4B)
API_KEY = load_api_key()
BASE_URL = load_base_url()
TEMPERATURE = 0.0

DATASET_FILE = "gretelaigretel_pii_masking_en_v1.parquet"
OUTPUT_DIR = "reports"
OUTPUT_FILENAME_BASE = "report.txt"

RUN_FULL_TEST = False
TEST_NUM_ROWS = 1000

RUN_MODEL_AUDITION = True
AUDITION_NUM_ROWS = 200

def get_file_name(prompt_type, audit=False):
    model_name = MODEL.split('/')[-1] if '/' in MODEL else MODEL
    safe_model_name = model_name.replace(':', '-').replace('.', '_')
    safe_prompt_type = prompt_type.replace('-', '_').replace(' ', '_')

    dynamic_filename = ""
    if audit:
        dynamic_filename = f"AUDIT_{safe_model_name}_temp{TEMPERATURE}_{safe_prompt_type}.txt"
    else:
        dynamic_filename = f"{safe_model_name}_temp{TEMPERATURE}_{safe_prompt_type}.txt"
    
    return dynamic_filename

def run_audit_for_model(client, dataset_path):
    audit_prompts = [
        ("zero_shot", prompts.get_zero_shot_prompt),
        ("few_shot", prompts.get_few_shot_prompt),
        ("chain_of_thought", prompts.get_chain_of_thought_prompt)
    ]

    output_dir_path = Path(OUTPUT_DIR)
    output_dir_path.mkdir(exist_ok=True)

    for label, prompt_fn in audit_prompts:
        print(f"\n=== Starting audit for prompt type: {label} ===")
        system_prompt, prompt_type = prompt_fn()

        report = test.full_test(
            client=client,
            dataset_path=dataset_path,
            num_rows_dataset=AUDITION_NUM_ROWS,
            temp=TEMPERATURE,
            system_prompt=system_prompt,
            model=MODEL
        )

        dynamic_filename = get_file_name(prompt_type, audit=True)

        output_path = output_dir_path / dynamic_filename

        original_stdout = sys.stdout
        with open(output_path, 'w', encoding='utf-8') as f:
            sys.stdout = f
            report_printer.print_report(report, prompt_type)
            report_printer.print_audits(report, max_items=100, show_raw=True, max_chars=2000)
        sys.stdout = original_stdout

        print(f"Audit report saved at: {output_path.resolve()}")

def run_full_test_for_model(client, dataset_path):
    system_prompt, prompt_type = prompts.get_zero_shot_prompt()
    report = test.full_test(
        client=client,
        dataset_path=dataset_path,
        num_rows_dataset=TEST_NUM_ROWS,
        temp=TEMPERATURE,
        system_prompt=system_prompt,
        model=MODEL
    )

    dynamic_filename = get_file_name(prompt_type, audit=False)

    output_dir_path = Path(OUTPUT_DIR)
    output_dir_path.mkdir(exist_ok=True)
    output_path = output_dir_path / dynamic_filename

    original_stdout = sys.stdout
    with open(output_path, 'w', encoding='utf-8') as f:
        sys.stdout = f
        report_printer.print_report(report, prompt_type)
    sys.stdout = original_stdout

    print(f"Test report saved at: {output_path.resolve()}")



if __name__ == "__main__":
    dataset_path = Path(__file__).parent / "tests" / "dataset" / DATASET_FILE
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"

    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    if RUN_FULL_TEST:
        run_full_test_for_model(client, dataset_path)
    
    if RUN_MODEL_AUDITION:
        run_audit_for_model(client, dataset_path)
