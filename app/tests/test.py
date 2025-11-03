import time
import pandas as pd
from utils import data_conversion_handler, metrics
import re

from tqdm import tqdm
import sys

def format_time(seconds):
    minutes = seconds / 60
    hours = minutes / 60
    return {
        "seconds": round(seconds, 2),
        "minutes": round(minutes, 2),
        "hours": round(hours, 2)
    }

def resolve_segmentation_errors(dataset_set, llm_set):   
    in_both, only_in_llm, only_in_dataset = metrics.compare_sets(dataset_set, llm_set)
    
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

def build_audit_from_artifacts(idx_1based, input_text, dataset_set, llm_str, llm_set):
    dataset_set_str = {str(x) for x in dataset_set}
    llm_set_str = {str(x) for x in llm_set}

    in_both, only_in_llm, only_in_dataset = metrics.compare_sets(dataset_set_str, llm_set_str)
    tp_adj, fp_adj, fn_adj = resolve_segmentation_errors(dataset_set_str, llm_set_str)

    return {
        "idx": int(idx_1based),
        "input_text": input_text,

        "dataset_set": sorted(dataset_set_str),
        "llm_str": llm_str,
        "llm_set": sorted(llm_set_str),

        "compare_strict": {
            "in_both": sorted(in_both),
            "only_in_llm": sorted(only_in_llm),
            "only_in_dataset": sorted(only_in_dataset),
        },

        "adjusted_counts": {
            "tp_adjusted": int(tp_adj),
            "fp_adjusted": int(fp_adj),
            "fn_adjusted": int(fn_adj),
        }
    }

def full_test(client, dataset_path, num_rows_dataset, temp, system_prompt, model, max_audits=200):
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

    audits = []

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

            if (fp > 0 or fn > 0) and len(audits) < max_audits:
                audit = build_audit_from_artifacts(
                    idx_1based=i,
                    input_text=row.text,
                    dataset_set=dataset_set,
                    llm_str=llm_str,
                    llm_set=llm_set
                )
                audits.append(audit)

            pbar.update(1)
    finally:
        pbar.close()

    total_model_pii_adjusted = tp_sum + fp_sum

    total_wall_time = time.perf_counter() - total_wall_time_start
    avg_llm_time = total_llm_time / total_rows if total_rows else 0.0
    f1 = metrics.compute_f1(tp_sum, fp_sum, fn_sum)

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

        "audits": audits
    }

    return report
