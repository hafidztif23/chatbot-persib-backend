import sys
sys.path.append(".")

from core.embeddings import semantic_search
import csv
import json

with open("queries.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

results = []

for item in queries:
    hits = semantic_search(item["query"], top_k=5)
    
    result_row = {
        "query": item["query"],
        "intent": item["intent"],
        "expected_source": item["expected_source"],
    }
    
    for i, hit in enumerate(hits):
        result_row[f"rank{i+1}_source"] = hit["source"]
        result_row[f"rank{i+1}_similarity"] = hit["similarity"]
        result_row[f"rank{i+1}_content_preview"] = hit["content"][:100]
        result_row[f"rank{i+1}_grade"] = ""
    
    results.append(result_row)
    print(f"Done: {item['query'][:50]}")

with open("retrieval_results_raw.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)