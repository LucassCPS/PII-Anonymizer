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

    print("\n==== False Negatives Breakdown by PII Class (FN) ====")
    missed_classes = report.get("missed_pii_class_breakdown", {})
    if missed_classes:
        sorted_missed = sorted(missed_classes.items(), key=lambda item: item[1], reverse=True)
        
        for class_name, count in sorted_missed:
            print(f"- {class_name}: {count}")
    else:
        print("No False Negatives recorded or breakdown data unavailable.")
    print("=====================================================\n")

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

def print_audits(report: dict, max_items: int = 10, show_raw: bool = True, max_chars: int = 800):
    audits = report.get("audits", [])
    total = len(audits)
    print("\n========== AUDIT SUMMARY ==========")
    print(f"Total audits collected (fp>0 or fn>0): {total}")
    if not audits:
        print("No audits collected.")
        print("===================================\n")
        return

    to_show = min(max_items, total)
    print(f"Showing first {to_show} audits:\n")

    for k in range(to_show):
        a = audits[k]
        print(f"--- Audit #{k+1} | Dataset line: {a['idx']} ---")
        print("Input:")
        print(f"  {a['input_text']}")

        print("Dataset set:")
        for item in a["dataset_set"]:
            print(f"  - {item}")

        print("LLM set:")
        if a["llm_set"]:
            for item in a["llm_set"]:
                print(f"  - {item}")
        else:
            print("  (empty)")

        cs = a["compare_strict"]
        print("Diff (strict):")
        print(f"  In both (TP): {len(cs['in_both'])}")
        print(f"  Only in LLM (FP): {len(cs['only_in_llm'])}")
        print(f"  Only in dataset (FN): {len(cs['only_in_dataset'])}")

        ac = a["adjusted_counts"]
        print(f"Adjusted counts → TP: {ac['tp_adjusted']} | FP: {ac['fp_adjusted']} | FN: {ac['fn_adjusted']}")

        if show_raw:
            raw = a.get("llm_str", "")
            raw_display = raw if len(raw) <= max_chars else (raw[:max_chars] + "... [truncated]")
            print("\nRaw LLM output:")
            print(raw_display)

        print()

    if total > to_show:
        print(f"... and {total - to_show} more not shown.")
    print("===================================\n")
