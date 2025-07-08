import json
import os

def load_all_faq_data(folder="data"):
    faq_all = []
    for fname in os.listdir(folder):
        if fname.endswith(".json"):
            with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    item["source"] = fname
                    faq_all.append(item)
    return faq_all