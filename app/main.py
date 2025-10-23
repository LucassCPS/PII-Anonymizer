from tests import test
from core.config import ModelEnum, load_model, load_api_key, load_base_url
from utils import prompts
from openai import OpenAI
from pathlib import Path

TEMPERATURES = [0.0 , 0.1, 0.2]
MODELS = load_model(ModelEnum.QWEN3_8B)
API_KEY = load_api_key()
BASE_URL = load_base_url()
SYSTEM_PROMPT = prompts.get_few_shot_prompt()
NUM_ROWS_DATASET = 20
DATASET_FILE = "gretelaigretel_pii_masking_en_v1.parquet"

if __name__ == "__main__":
    dataset_path = Path(__file__).parent / "tests" / "dataset" / DATASET_FILE
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    report = test.full_test(client=client, 
                            dataset_path=dataset_path,
                            num_rows_dataset=NUM_ROWS_DATASET,
                            temp=TEMPERATURES[0],
                            system_prompt=SYSTEM_PROMPT,
                            model=MODELS)

    test.print_report(report)