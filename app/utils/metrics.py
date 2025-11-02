def compare_sets(dataset_set, llm_set_response):
    only_in_dataset = dataset_set - llm_set_response   # FN
    only_in_llm = llm_set_response - dataset_set       # FP
    in_both = dataset_set & llm_set_response           # TP
    return in_both, only_in_llm, only_in_dataset

def compute_f1(tp, fp, fn):
    denom = (2 * tp + fp + fn)
    return (2 * tp / denom) if denom else 0.0