import time
import pandas as pd
from utils import data_conversion_handler

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

        output = response.choices[0].message.content.strip() if response else ""
        output = output if output else '{ "entities": [] }'
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

    for idx, row in df.iterrows():
        if idx >= total_rows:
            break

        dataset_json = data_conversion_handler.string_list_to_json(row["entities"])
        dataset_set = data_conversion_handler.dataset_json_to_set(dataset_json)
        total_dataset_pii += len(dataset_set)

        llm_str, call_time = call_llm(client, model, system_prompt, row["text"], temp)
        total_llm_time += call_time

        llm_json = data_conversion_handler.string_list_to_json(llm_str)
        llm_set = data_conversion_handler.llm_json_to_set(llm_json)

        # empty responses (usually the LLM couldn't get to a proper response)
        if not llm_set:
            total_no_response += 1

        total_llm_pii += len(llm_set)

        in_both, only_in_llm, only_in_dataset = compare_sets(dataset_set, llm_set)
        tp_sum += len(in_both)
        fp_sum += len(only_in_llm)
        fn_sum += len(only_in_dataset)

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
        "total_missed_pii": int(fn_sum),

        "total_no_response": int(total_no_response),

        "tp": int(tp_sum),
        "fp": int(fp_sum),
        "fn": int(fn_sum),

        "precision": round(tp_sum / (tp_sum + fp_sum), 6) if (tp_sum + fp_sum) else 0.0,
        "recall": round(tp_sum / (tp_sum + fn_sum), 6) if (tp_sum + fn_sum) else 0.0,
        "f1_score": round(f1, 6),
    }

    return report


def print_report(report: dict):
    print("\n==== Test Execution Report ====")
    print(f"Model: {report['model']}")
    print(f"Temperature: {report['temperature']}")
    print(f"Dataset rows used: {report['dataset_rows_used']}\n")

    print("---- Execution Time ----")
    print(f"Total time: {report['total_time']['seconds']} s "
          f"({report['total_time']['minutes']} min / {report['total_time']['hours']} h)")
    print(f"Average LLM call time: {report['avg_llm_call_time']['seconds']} s "
          f"({report['avg_llm_call_time']['minutes']} min / {report['avg_llm_call_time']['hours']} h)\n")

    print("---- Sensitive Information ----")
    print(f"Total PII in dataset (expected): {report['total_dataset_pii']}")
    print(f"Total PII detected by model: {report['total_model_pii']}")
    print(f"Total missed PII: {report['total_missed_pii']}")
    print(f"Total LLM empty responses (no entities found): {report['total_no_response']}\n")

    print("---- Detection Metrics ----")
    print(f"True Positives (TP): {report['tp']}   = correctly identified PII items")
    print(f"False Positives (FP): {report['fp']}  = model detected items not in the dataset")
    print(f"False Negatives (FN): {report['fn']}  = model missed items that exist in the dataset\n")

    print(f"Precision: {report['precision']}")
    print(f"Recall: {report['recall']}")
    print(f"F1-score: {report['f1_score']}")
    print("================================\n")
