# GetData.py
import json
import re
from pathlib import Path
from typing import Dict
from Create_json import create_json

def load_str_blocks(save_dir: str) -> Dict[str, str]:
    """
    #1) Description:
    --> Creating json files (including data inside with utf-8) from Create_json.py
    --> Load Str blocks the program will edit
    --> The value would be stored in ["root"]["properties"]["AllStyleValues_0"]["Str"]
    

    #2) e.g Return value:
    {
        "Skin": "....;type:Skin;",
        "Hair": "....;type:Hair;",
        "Hat":  "....;type:Hat;",
        ...
    }
    """
    # 1) Creating .json via Create_json.py
    # --> created list would be the list of the ***path***
    created = create_json(save_dir)  
    if not created:
        raise FileNotFoundError("characterStyle-1.0.json creation failed")

    json_path = created[0]  
    # *** There should be only one characterStyle-1.0.json ***
    if not Path(json_path).exists():
        raise FileNotFoundError(f"No json file exists: {json_path}")

    # 2) JSON loading
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    s = data["root"]["properties"]["AllStyleValues_0"]["Str"]

    # 3) Blocks
    results: Dict[str, str] = {}
    """
    --> hint for format of results
    --> Thats why imported Dict 
    """
    prev_end = 0
    for m in re.finditer(r";type:([^;]+)", s):
        typ = m.group(1).strip()
        block = s[prev_end:m.end()]  
        results[typ] = block
        prev_end = m.end()

    return results

# -------------------------
# Testing
# -------------------------
if __name__ == "__main__":
    save_dir = r"C:\Users\PC\AppData\Local\Longvinter\Saved\SaveGames"
    blocks = load_str_blocks(save_dir)
    for t, b in blocks.items():
        print(f"[{t}]")
        print(b)
        print("-" * 50)
