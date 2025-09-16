# GetData.py
import json
import re
from pathlib import Path
from typing import Dict
from Create_json import create_json

def load_str_blocks(save_dir: str) -> Dict[str, str]:
    """
    SaveGames 디렉터리를 받아, Create_json.create_json()을 이용해
    characterStyle-1.0.json 파일을 생성/갱신하고
    JSON 안의 ["root"]["properties"]["AllStyleValues_0"]["Str"] 값을
    type별 블록으로 잘라 반환.

    반환 예시:
    {
        "Skin": "....;type:Skin;",
        "Hair": "....;type:Hair;",
        "Hat":  "....;type:Hat;",
        ...
    }
    """
    # 1) JSON 생성
    created = create_json(save_dir)  # Path 리스트 반환
    if not created:
        raise FileNotFoundError("characterStyle-1.0.json 생성 실패")

    json_path = created[0]  # 첫 번째 JSON 경로 사용
    if not Path(json_path).exists():
        raise FileNotFoundError(f"JSON 파일 없음: {json_path}")

    # 2) JSON 로드
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    s = data["root"]["properties"]["AllStyleValues_0"]["Str"]

    # 3) type별 블록 추출
    results: Dict[str, str] = {}
    prev_end = 0
    for m in re.finditer(r";type:([^;]+)", s):
        typ = m.group(1).strip()
        block = s[prev_end:m.end()]  # 블록 = 이전 구간부터 type 토큰 끝까지
        results[typ] = block
        prev_end = m.end()

    return results

# -------------------------
# 사용 예시
# -------------------------
if __name__ == "__main__":
    save_dir = r"C:\Users\PC\AppData\Local\Longvinter\Saved\SaveGames"
    blocks = load_str_blocks(save_dir)
    for t, b in blocks.items():
        print(f"[{t}]")
        print(b)
        print("-" * 50)
