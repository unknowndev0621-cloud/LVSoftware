# Main_free.py  (Distribution build - no Hat controls, user picks SAVE_DIR at startup)

from __future__ import annotations

import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog
from typing import Optional, Tuple, Dict

# ---- 외부 모듈 ---------------------------------------------------------------
from Create_json import create_json
from Update_json import (
    read_json_str, parse_str, get_last_field,
    update_skin_rgb, update_hair_rgb, set_baldy_mode,
)
from SaveApply import apply_json_to_sav

# ---- 상수 / 정규식 -----------------------------------------------------------
# 고정 경로 삭제! 시작 시 유저가 선택 -> 아래 전역 변수에 주입
SAVE_DIR: Optional[Path] = None
JSON_FILE: Optional[Path] = None

RGBA_RE = re.compile(r"\(R=([0-9.]+),G=([0-9.]+),B=([0-9.]+),A=[0-9.]+\)")

# ---- 유틸 함수 ---------------------------------------------------------------
def ensure_json_exists() -> None:
    """sav -> json 변환 시도 (json 이미 있으면 그대로 둠)"""
    if not SAVE_DIR:
        return
    try:
        create_json(str(SAVE_DIR))
    except Exception as e:
        print("[WARN] create_json failed:", e)


def rgba_str_to_rgb255(rgba: str) -> Optional[Tuple[int, int, int]]:
    """'(R=...,G=...,B=...,A=...)' -> (r,g,b) 0~255. 실패 시 None."""
    m = RGBA_RE.match(rgba or "")
    if not m:
        return None
    r = max(0, min(255, int(round(float(m.group(1)) * 255))))
    g = max(0, min(255, int(round(float(m.group(2)) * 255))))
    b = max(0, min(255, int(round(float(m.group(3)) * 255))))
    return (r, g, b)


def rgb255_to_rgba_str(rgb: Tuple[int, int, int]) -> str:
    """(r,g,b) 0~255 -> (R=...,G=...,B=...,A=1.000000)"""
    r, g, b = rgb
    return f"(R={round(r/255,6)},G={round(g/255,6)},B={round(b/255,6)},A=1.000000)"


def read_current_values() -> Dict[str, Dict[str, str]]:
    """
    JSON에서 현재 값 읽기 (배포용: Hat 정보는 다루지 않음)
    반환: {"Skin":{"color":...}, "Hair":{"color":...}}
    """
    if not JSON_FILE:
        return {"Skin": {"color": ""}, "Hair": {"color": ""}}
    s, _ = read_json_str(JSON_FILE)
    _, blocks, _ = parse_str(s)
    vals = {"Skin": {"color": ""}, "Hair": {"color": ""}}
    if "Skin" in blocks:
        vals["Skin"]["color"] = get_last_field(blocks["Skin"], "color")
    if "Hair" in blocks:
        vals["Hair"]["color"] = get_last_field(blocks["Hair"], "color")
    return vals


# ---- 소형 위젯: 컬러 미리보기 -------------------------------------------------
class ColorPreview(tk.Canvas):
    """(R,G,B,A) 문자열을 받아 사각형으로 미리보기 표시. 실패 시 '?' 표시."""
    def __init__(self, parent, width=40, height=40):
        super().__init__(parent, width=width, height=height, bd=1, relief="solid")

    def set_color_text(self, rgba_text: str) -> None:
        self.delete("all")
        rgb = rgba_str_to_rgb255(rgba_text)
        if rgb is None:
            self.create_text(20, 20, text="?", font=("Segoe UI", 12))
        else:
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.create_rectangle(2, 2, 38, 38, fill=hex_color, outline="")


# ---- 메인 앱 ------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Longvinter Color Changer [Free Edition] -Made By Unknown-")
        self.geometry("680x300")

        # 1) 시작하자마자 저장 폴더 선택
        self._pick_save_dir_at_start()

        # 2) 데이터 확보
        ensure_json_exists()
        if not JSON_FILE or not JSON_FILE.exists():
            messagebox.showerror("Error", f"JSON file not found:\n{JSON_FILE}")
            self.destroy()
            return

        self.initial = read_current_values()  # 원본 상태(비교/표시용)

        # 바인딩 변수
        self.skin_var = tk.StringVar(value=self.initial["Skin"]["color"])
        self.hair_var = tk.StringVar(value=self.initial["Hair"]["color"])

        # ➜ BALDY MODE: 즉시 저장 X, 저장 시에만 적용
        self.baldy_mode = tk.BooleanVar(value=False)

        # UI
        self._build_ui()

    def _pick_save_dir_at_start(self) -> None:
        """폴더 선택 대화상자 → SAVE_DIR/JSON_FILE 설정"""
        global SAVE_DIR, JSON_FILE
        path = filedialog.askdirectory(title="Select Longvinter Save Folder")
        if not path:
            messagebox.showwarning("Select Folder", "Save 폴더를 선택하지 않아 종료합니다.")
            self.destroy()
            return
        SAVE_DIR = Path(path)
        JSON_FILE = SAVE_DIR / "characterStyle-1.0.json"

    # --- UI 빌드 ---
    def _build_ui(self) -> None:
        y = 18
        self._build_skin_row(y);  y += 90
        self._build_hair_row(y);  y += 90

        # BALDY 상태 안내 라벨
        self.baldy_status = tk.Label(self, text="BALDY MODE: OFF (Toggle)", fg="#a00", font=("Segoe UI", 9, "bold"))
        self.baldy_status.place(x=16, y=y-6)

        bar = tk.Frame(self)
        bar.pack(side="bottom", fill="x", pady=8)

        self.baldy_btn = tk.Button(bar, text="BALDY MODE: OFF (Toggle)", command=self.on_toggle_baldy)
        self.baldy_btn.pack(side="left", padx=8)

        tk.Button(bar, text="Save (JSON → SAV)", command=self.on_save).pack(side="left", padx=8)
        tk.Button(bar, text="Refresh", command=self.on_refresh).pack(side="left", padx=8)
        tk.Button(bar, text="Exit", command=self.destroy).pack(side="right", padx=8)

    def _build_skin_row(self, y: int) -> None:
        frm = tk.Frame(self); frm.place(x=14, y=y, width=630, height=80)
        tk.Label(frm, text="Skin Colour", font=("Segoe UI", 10, "bold")).place(x=0, y=0)

        # 읽기 전용 표시
        tk.Entry(frm, textvariable=self.skin_var, width=64, state="readonly").place(x=0, y=26)

        # 미리보기 + 선택
        self.skin_preview = ColorPreview(frm); self.skin_preview.place(x=540, y=14)
        self.skin_preview.set_color_text(self.skin_var.get())
        tk.Button(frm, text="Edit", command=lambda: self._choose_color(self.skin_var, self.skin_preview)).place(x=470, y=23)

        tk.Label(frm, text="Pick a colour with the RGB selector. ⚠️ If you don't change it, the original is kept.",
                 fg="#666", font=("Segoe UI", 8), justify="left", wraplength=480).place(x=0, y=52)

    def _build_hair_row(self, y: int) -> None:
        frm = tk.Frame(self); frm.place(x=14, y=y, width=630, height=80)
        tk.Label(frm, text="Hair Colour", font=("Segoe UI", 10, "bold")).place(x=0, y=0)

        tk.Entry(frm, textvariable=self.hair_var, width=64, state="readonly").place(x=0, y=26)

        self.hair_preview = ColorPreview(frm); self.hair_preview.place(x=540, y=14)
        self.hair_preview.set_color_text(self.hair_var.get())
        tk.Button(frm, text="Edit", command=lambda: self._choose_color(self.hair_var, self.hair_preview)).place(x=470, y=23)

        tk.Label(frm, text="Pick a colour with the RGB selector. ⚠️ If you don't change it, the original is kept.",
                 fg="#666", font=("Segoe UI", 8), justify="left", wraplength=480).place(x=0, y=52)

    # --- 이벤트 핸들러 ---
    def _choose_color(self, var: tk.StringVar, preview: ColorPreview) -> None:
        """RGB 선택기 -> (R,G,B,A) 문자열로 표시값만 갱신"""
        rgb, _ = colorchooser.askcolor(title="RGB Selector")
        if not rgb:
            return
        rgba_text = rgb255_to_rgba_str((int(rgb[0]), int(rgb[1]), int(rgb[2])))
        var.set(rgba_text)
        preview.set_color_text(rgba_text)

    def on_toggle_baldy(self) -> None:
        """BALDY MODE 토글: 즉시 저장하지 않고 플래그만 바꿈"""
        new_val = not self.baldy_mode.get()
        self.baldy_mode.set(new_val)
        if new_val:
            self.baldy_btn.config(text="BALDY MODE: ON (Toggle)", relief="sunken")
            self.baldy_status.config(text="BALDY MODE: ON", fg="#060")
        else:
            self.baldy_btn.config(text="BALDY MODE: OFF (Toggle)", relief="raised")
            self.baldy_status.config(text="BALDY MODE: OFF (Toggle)", fg="#a00")

    def on_refresh(self) -> None:
        """디스크의 최신 JSON 값을 다시 읽어 표시 (대기 중인 변경은 초기화)"""
        ensure_json_exists()
        if not JSON_FILE or not JSON_FILE.exists():
            messagebox.showerror("Error", f"JSON file not found:\n{JSON_FILE}")
            return

        self.initial = read_current_values()
        self.skin_var.set(self.initial["Skin"]["color"])
        self.hair_var.set(self.initial["Hair"]["color"])

        self.skin_preview.set_color_text(self.skin_var.get())
        self.hair_preview.set_color_text(self.hair_var.get())

        # BALDY 플래그도 초기화
        self.baldy_mode.set(False)
        self.baldy_btn.config(text="BALDY MODE: OFF (Toggle)", relief="raised")
        self.baldy_status.config(text="BALDY MODE: OFF (Toggle)", fg="#a00")

    def on_save(self) -> None:
        """
        변경 사항 저장(일괄 적용):
        - Skin/Hair: 선택한 색상 적용
        - BALDY MODE가 ON이면 Hair.definitionid를 빈 값으로 설정
        이후 SAV로 반영.
        """
        try:
            ensure_json_exists()
            if not JSON_FILE or not JSON_FILE.exists():
                messagebox.showerror("Error", f"JSON file not found:\n{JSON_FILE}")
                return

            # Skin
            skin_rgb = rgba_str_to_rgb255(self.skin_var.get().strip())
            if skin_rgb is not None:
                update_skin_rgb(JSON_FILE, *skin_rgb)

            # Hair
            hair_rgb = rgba_str_to_rgb255(self.hair_var.get().strip())
            if hair_rgb is not None:
                update_hair_rgb(JSON_FILE, *hair_rgb)

            # ➜ BALDY MODE (저장 시에만 적용)
            if self.baldy_mode.get():
                set_baldy_mode(JSON_FILE)

            # SAV 반영
            if SAVE_DIR:
                apply_json_to_sav(SAVE_DIR)
            else:
                messagebox.showwarning("Select Folder", "Save 폴더를 먼저 선택해 주세요.")
                return

            # 저장 완료 후 BALDY 플래그 끔
            self.baldy_mode.set(False)
            self.baldy_btn.config(text="BALDY MODE: OFF (Toggle)", relief="raised")
            self.baldy_status.config(text="BALDY MODE: OFF (Toggle)", fg="#a00")

            messagebox.showinfo("Done", "Skin/Hair updated.\nRejoin the server to see changes.")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{e}")


# ---- 엔트리 포인트 ------------------------------------------------------------
if __name__ == "__main__":
    App().mainloop()
