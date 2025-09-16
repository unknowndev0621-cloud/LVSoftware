# StrModel.py
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Union

TYPE_RE = re.compile(r";type:([^;]+)")
FIELD_RE_TMPL = r"{name}:([^;]*)"

# -------- 파서/빌더의 핵심: 원본 순서 + tail 보존 --------
def parse_str(s: str) -> Tuple[List[str], Dict[str, str], str]:
    """
    Str 전체를 파싱하여:
    - order: type 등장 순서 (예: ["Skin", "Hat", "Hair", ...])
    - blocks: type별 블록 문자열 (각 블록은 '...;type:<TYPE>'까지 포함)
    - tail: 마지막 ;type:<TYPE> 뒤에 남는 꼬리 문자열
    """
    order: List[str] = []
    blocks: Dict[str, str] = {}

    prev_end = 0
    last_m = None
    for m in TYPE_RE.finditer(s):
        typ = m.group(1).strip()
        order.append(typ)
        # 블록: 이전 경계 ~ 이번 type 토큰 끝
        blocks[typ] = s[prev_end:m.end()]
        prev_end = m.end()
        last_m = m

    tail = s[prev_end:] if last_m else ""  # 마지막 type 뒤 tail 보존
    return order, blocks, tail

def build_str(order: List[str], blocks: Dict[str, str], tail: str) -> str:
    """원래 순서대로 블록을 이어 붙이고 tail을 덧붙여 Str 재구성"""
    return "".join(blocks[t] for t in order if t in blocks) + tail

# -------- 블록 내부의 필드 읽기/교체 --------
def get_last_field(block: str, field: str) -> str:
    """block 내에서 field:VALUE 의 마지막 값을 읽어 반환. 없으면 빈 문자열."""
    last = ""
    pattern = re.compile(FIELD_RE_TMPL.format(name=re.escape(field)))
    for m in pattern.finditer(block):
        last = m.group(1).strip()
    return last

def replace_last_field(block: str, field: str, new_value: str) -> str:
    """
    block 내에서 field:VALUE 의 마지막 항목만 new_value로 교체.
    없으면 ;type:<TYPE> '앞'에 안전하게 삽입한다.
    """
    pattern = re.compile(FIELD_RE_TMPL.format(name=re.escape(field)))
    matches = list(pattern.finditer(block))
    if matches:
        last = matches[-1]
        return block[:last.start()] + f"{field}:{new_value}" + block[last.end():]

    # 필드가 없으면 ;type:<TYPE> 바로 앞에 삽입
    m_type = re.search(r";type:[^;]+", block)
    if not m_type:  # 비정상: type 토큰이 없으면 맨 끝에 추가
        prefix = block if block.endswith(";") else (block + ";")
        return prefix + f"{field}:{new_value};"

    insert_at = m_type.start()
    prefix = block[:insert_at]
    suffix = block[insert_at:]
    if not prefix.endswith(";"):
        prefix += ";"
    return prefix + f"{field}:{new_value};" + suffix

# -------- RGB 유틸 --------
def rgba_str_from_255(r: int, g: int, b: int) -> str:
    """0~255 RGB -> (R=...,G=...,B=...,A=1.000000)"""
    r_f = round(max(0, min(255, r)) / 255, 6)
    g_f = round(max(0, min(255, g)) / 255, 6)
    b_f = round(max(0, min(255, b)) / 255, 6)
    return f"(R={r_f},G={g_f},B={b_f},A=1.000000)"

# -------- JSON I/O --------
def read_json_str(json_path: Union[str, Path]) -> str:
    with Path(json_path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["root"]["properties"]["AllStyleValues_0"]["Str"], data

def write_json_str(json_path: Union[str, Path], data: dict, new_str: str) -> None:
    data["root"]["properties"]["AllStyleValues_0"]["Str"] = new_str
    with Path(json_path).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------- 고수준 API: Hat/Skin/Hair만 수정, 나머지는 그대로 --------
def update_skin_rgb(json_path: Union[str, Path], r: int, g: int, b: int) -> None:
    s, data = read_json_str(json_path)
    order, blocks, tail = parse_str(s)
    if "Skin" not in blocks:
        raise ValueError("Skin 블록이 없습니다.")
    blocks["Skin"] = replace_last_field(blocks["Skin"], "color", rgba_str_from_255(r, g, b))
    write_json_str(json_path, data, build_str(order, blocks, tail))

def update_hair_rgb(json_path: Union[str, Path], r: int, g: int, b: int) -> None:
    s, data = read_json_str(json_path)
    order, blocks, tail = parse_str(s)
    if "Hair" not in blocks:
        raise ValueError("Hair 블록이 없습니다.")
    blocks["Hair"] = replace_last_field(blocks["Hair"], "color", rgba_str_from_255(r, g, b))
    write_json_str(json_path, data, build_str(order, blocks, tail))

def update_hat(json_path: Union[str, Path], color_str: str, fx_str: str) -> None:
    """
    Hat의 color는 '문자열 그대로', fx는 'fx:값;'의 값 부분만 교체.
    둘 중 하나만 바꾸고 싶으면 기존 값을 읽어서 그대로 넘기면 됨.
    """
    s, data = read_json_str(json_path)
    order, blocks, tail = parse_str(s)
    if "Hat" not in blocks:
        raise ValueError("Hat 블록이 없습니다.")
    blk = blocks["Hat"]
    cur_color = get_last_field(blk, "color")
    cur_fx    = get_last_field(blk, "fx")

    # 인자가 빈 문자열이면 그대로 유지하고 싶을 수 있으니, 호출부에서 명시적으로 cur_*를 넘기면 됨
    color_final = color_str.strip() if color_str is not None else cur_color
    fx_final    = fx_str.strip() if fx_str is not None else cur_fx

    blk = replace_last_field(blk, "color", color_final)
    blk = replace_last_field(blk, "fx", fx_final)
    blocks["Hat"] = blk

    write_json_str(json_path, data, build_str(order, blocks, tail))


def set_baldy_mode(json_path: Union[str, Path]) -> None:
    """
    Hair 블록의 definitionid 값을 비워서 "definitionid:;" 상태로 만듭니다.
    다른 필드는 건드리지 않습니다.
    """
    s, data = read_json_str(json_path)
    order, blocks, tail = parse_str(s)
    if "Hair" not in blocks:
        raise ValueError("Hair 블록이 없습니다.")
    blk = blocks["Hair"]
    blk = replace_last_field(blk, "definitionid", "")
    blocks["Hair"] = blk
    write_json_str(json_path, data, build_str(order, blocks, tail))
