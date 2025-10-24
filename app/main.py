from tests import test
from core.config import ModelEnum, load_model, load_api_key, load_base_url
from utils import prompts
from openai import OpenAI
from pathlib import Path
import sys

TEMPERATURES = [0.0 , 0.1, 0.2]
MODEL = load_model(ModelEnum.SMOLL3_Q4)
API_KEY = load_api_key()
BASE_URL = load_base_url()
NUM_ROWS_DATASET = 1000
DATASET_FILE = "gretelaigretel_pii_masking_en_v1.parquet"

OUTPUT_DIR = "reports"
OUTPUT_FILENAME_BASE = "report.txt"

if __name__ == "__main__":
    dataset_path = Path(__file__).parent / "tests" / "dataset" / DATASET_FILE
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    system_prompt, prompt_type = prompts.get_zero_shot_prompt()
    temp_value = TEMPERATURES[0]

    report = test.full_test(client=client, 
                            dataset_path=dataset_path,
                            num_rows_dataset=NUM_ROWS_DATASET,
                            temp=temp_value,
                            system_prompt=system_prompt,
                            model=MODEL)
   
    model_name = MODEL.split('/')[-1] if '/' in MODEL else MODEL
    safe_model_name = model_name.replace(':', '-').replace('.', '_')
    safe_prompt_type = prompt_type.replace('-', '_').replace(' ', '_')
    dynamic_filename = f"{safe_model_name}_temp{temp_value}_{safe_prompt_type}.txt"
    
    output_dir_path = Path(OUTPUT_DIR)
    output_dir_path.mkdir(exist_ok=True)
    output_path = output_dir_path / dynamic_filename
    
    original_stdout = sys.stdout 
    with open(output_path, 'w', encoding='utf-8') as f:
        sys.stdout = f
        test.print_report(report, prompt_type) 

    sys.stdout = original_stdout 
    print(f"Report saved at: {output_path.resolve()}")
