import time
import pandas as pd
from utils import data_conversion_handler
import re

from tqdm import tqdm
import sys

def resolve_segmentation_errors(dataset_set, llm_set):   
    in_both, only_in_llm, only_in_dataset = compare_sets(dataset_set, llm_set)
    
    tp_adjusted = len(in_both)
    fp_adjusted = len(only_in_llm)
    fn_adjusted = len(only_in_dataset)

    llm_missed_pii = list(only_in_dataset)
    llm_extra_pii = only_in_llm.copy() 
    
    for fn_item in llm_missed_pii:
        fn_canonical = re.sub(r'[\s,.-]', '', fn_item).lower()

        possible_llm_components = []
        for fp_item in llm_extra_pii:
            if str(fp_item) in fn_item:
                possible_llm_components.append(fp_item)
                
        if possible_llm_components:
            possible_llm_components.sort(key=lambda x: fn_item.find(x))

            llm_combined_string = ' '.join(possible_llm_components)
            
            llm_combined_canonical = re.sub(r'[\s,.-]', '', llm_combined_string).lower()

            if llm_combined_canonical == fn_canonical:
                tp_adjusted += 1
                fn_adjusted -= 1
                fp_adjusted -= len(possible_llm_components)

                for component in possible_llm_components:
                    if component in llm_extra_pii:
                         llm_extra_pii.remove(component)

    return tp_adjusted, fp_adjusted, fn_adjusted

def call_llm(client, model, system_prompt, input_text, temp):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text}
    ]

    try:
        t0 = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp
        )
        dt = time.perf_counter() - t0

        output = response.choices[0].message.content.strip() if response else '{ "entities": [] }'
        return output, dt
    except Exception:
        return '{ "entities": [] }', 0.0

def compare_sets(dataset_set, llm_set_response):
    only_in_dataset = dataset_set - llm_set_response   # FN
    only_in_llm = llm_set_response - dataset_set       # FP
    in_both = dataset_set & llm_set_response           # TP
    return in_both, only_in_llm, only_in_dataset

def compute_f1(tp, fp, fn):
    denom = (2 * tp + fp + fn)
    return (2 * tp / denom) if denom else 0.0

def full_test(client, dataset_path, num_rows_dataset, temp, system_prompt, model):
    df = pd.read_parquet(dataset_path)
    total_rows = min(num_rows_dataset, len(df))

    total_llm_time = 0.0
    total_wall_time_start = time.perf_counter()

    total_dataset_pii = 0
    total_llm_pii = 0
    total_no_response = 0
    tp_sum = 0
    fp_sum = 0
    fn_sum = 0

    invalid_responses = []
    invalid_response_line_texts = []

    pbar = tqdm(
        total=total_rows,
        desc="Executando testes",
        unit="linha",
        file=sys.stdout,
        dynamic_ncols=True,
        mininterval=0.1,
        miniters=1,
        disable=False,
        ascii=True,
        leave=True,
        bar_format="{l_bar}{bar}{r_bar}"
    )
    pbar.refresh()

    try:
        for i, row in enumerate(df.itertuples(index=False), start=1):
            if i > total_rows:
                break

            dataset_json = data_conversion_handler.string_list_to_json(row.entities)
            dataset_set = data_conversion_handler.dataset_json_to_set(dataset_json)
            total_dataset_pii += len(dataset_set)

            llm_str, call_time = call_llm(client, model, system_prompt, row.text, temp)
            total_llm_time += call_time

            llm_clean_resp = data_conversion_handler.clean_llm_response(llm_str)
            llm_json = data_conversion_handler.string_list_to_json(llm_clean_resp)
            llm_set = data_conversion_handler.llm_json_to_set(llm_json)

            if not llm_set:
                total_no_response += 1
                invalid_responses.append(i)
                invalid_response_line_texts.append(row.text)
            total_llm_pii += len(llm_set)

            tp, fp, fn = resolve_segmentation_errors(dataset_set, llm_set)
            tp_sum += tp; fp_sum += fp; fn_sum += fn

            pbar.update(1)
    finally:
        pbar.close()

    total_model_pii_adjusted = tp_sum + fp_sum

    total_wall_time = time.perf_counter() - total_wall_time_start
    avg_llm_time = total_llm_time / total_rows if total_rows else 0.0
    f1 = compute_f1(tp_sum, fp_sum, fn_sum)

    def format_time(seconds):
        minutes = seconds / 60
        hours = minutes / 60
        return {
            "seconds": round(seconds, 2),
            "minutes": round(minutes, 2),
            "hours": round(hours, 2)
        }

    report = {
        "model": model,
        "temperature": temp,
        "dataset_rows_used": total_rows,

        "total_time": format_time(total_wall_time),
        "avg_llm_call_time": format_time(avg_llm_time),

        "total_dataset_pii": int(total_dataset_pii),
        "total_model_pii": int(total_llm_pii),
        "total_model_pii_adjusted":  int(total_model_pii_adjusted),
        "total_missed_pii": int(fn_sum),

        "total_no_response": int(total_no_response),

        "invalid_response_lines": invalid_responses,
        "invalid_response_texts": invalid_response_line_texts,

        "tp": int(tp_sum),
        "fp": int(fp_sum),
        "fn": int(fn_sum),

        "precision": round(tp_sum / (tp_sum + fp_sum), 6) if (tp_sum + fp_sum) else 0.0,
        "recall": round(tp_sum / (tp_sum + fn_sum), 6) if (tp_sum + fn_sum) else 0.0,
        "f1_score": round(f1, 6),
    }

    return report

def print_report(report, prompt_type):
    print("==== Test Execution Report ====")
    print(f"Model: {report['model']}")
    print(f"Prompt technique: {prompt_type}")
    print(f"Temperature: {report['temperature']}")
    print(f"Dataset rows used: {report['dataset_rows_used']}\n")

    print("---- Execution Time ----")
    print(f"Total time: {report['total_time']['seconds']} s "
          f"({report['total_time']['minutes']} min / {report['total_time']['hours']} h)")
    print(f"Average LLM call time: {report['avg_llm_call_time']['seconds']} s "
          f"({report['avg_llm_call_time']['minutes']} min / {report['avg_llm_call_time']['hours']} h)")

    print("---- Sensitive Information ----")
    print(f"Total PII in dataset (expected): {report['total_dataset_pii']}")
    print(f"Total PII detected by model: {report['total_model_pii']}")
    print(f"Total PII detected by model (adjusted): {report['total_model_pii_adjusted']}")
    print(f"Total missed PII: {report['total_missed_pii']}")
    print(f"Total LLM empty responses: {report['total_no_response']}\n")

    print("---- Detection Metrics ----")
    print(f"True Positives (TP): {report['tp']}   = correctly identified PII items")
    print(f"False Positives (FP): {report['fp']}  = model detected items not in the dataset")
    print(f"False Negatives (FN): {report['fn']}  = model missed items that exist in the dataset\n")

    print(f"Precision: {report['precision']}")
    print(f"Recall: {report['recall']}")
    print(f"F1-score: {report['f1_score']}")
    print("================================\n")

    print("\n==== Dataset Lines That Returned an Empty JSON Response ====")
    if report.get("invalid_response_lines"):
        print("---- Empty Response Tracking ----")
        total_empty_responses = len(report['invalid_response_lines'])
        print(f"Line that returned the empty response: {report['invalid_response_lines']}")
        
        print("\nText contents that returned the empty response (first 10):")
        for i, text in enumerate(report['invalid_response_texts']):
            if i >= 10: 
                print(f"... and {total_empty_responses - 10} more.")
                break
            print(f"\n  Line {report['invalid_response_lines'][i]}: '{text}'") 
        print("\n")
    else:
        print("No lines returned the exact empty JSON response string.")
    print("================================\n")