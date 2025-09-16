# SaveApply.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import os
BACKUP_ON_SAVE = False  # ← 백업 비활성화
# Create_json.py 에서 uesave 경로를 그대로 가져와 재사용
try:
    from Create_json import UESAVE  # BASE / ("uesave.exe" or "uesave")
except Exception:
    # 백업: 같은 폴더/현재 작업 디렉토리에서 uesave를 찾아본다
    HERE = Path(__file__).resolve().parent
    UESAVE = (
        HERE / "uesave.exe" if os.name == "nt" else HERE / "uesave"
    )
    if not UESAVE.exists():
        UESAVE = Path("uesave.exe" if os.name == "nt" else "uesave")  # PATH 의존


def _backup(file: Path) -> Path | None:
    """기존 sav가 있으면 안전하게 백업 파일로 이름 변경"""
    if not BACKUP_ON_SAVE:
        return None
    if not file.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = file.with_suffix(file.suffix + f".bak.{ts}")
    file.rename(bak)
    print(f"[backup] {file.name} -> {bak.name}")
    return bak


def _from_json_to_sav(json_path: Path, out_sav: Path) -> None:
    """
    uesave를 사용해 JSON -> SAV 변환.
    uesave 빌드마다 인자 스타일이 달 수 있어 두 가지 시도.
    """
    cmds = [
        [str(UESAVE), "from-json", "--input", str(json_path), "--output", str(out_sav)],
        [str(UESAVE), "from-json", str(json_path), str(out_sav)],
    ]
    last_err = None
    for cmd in cmds:
        try:
            print("[exec]", " ".join(cmd))
            subprocess.check_call(cmd)
            return
        except subprocess.CalledProcessError as e:
            last_err = e
    raise RuntimeError(f"from-json failed with uesave: {last_err}")


def apply_json_to_sav(save_dir: str | Path, basename: str = "characterStyle-1.0") -> Path:
    """
    SaveGames 디렉터리에서 <basename>.json 을 읽어 같은 이름의 <basename>.sav 로 덮어쓰기.
    - 기존 sav는 자동 백업 (*.sav.bak.YYYYMMDD_HHMMSS)
    - 반환: 새로 쓴 sav 경로
    """
    save_dir = Path(save_dir)
    json_path = save_dir / f"{basename}.json"
    sav_path = save_dir / f"{basename}.sav"

    if not json_path.exists():
        raise FileNotFoundError(f"JSON not found: {json_path}")

    

    # 변환 실행
    _from_json_to_sav(json_path, sav_path)
    if not sav_path.exists():
        raise RuntimeError("SAV write failed (file not created).")

    print(f"[ok] wrote: {sav_path}")
    return sav_path


def apply_json_file(json_path: str | Path) -> Path:
    """
    JSON 파일 경로를 직접 받아, 같은 폴더/같은 이름의 .sav 로 덮어쓰기.
    - 기존 sav는 자동 백업
    - 반환: 새로 쓴 sav 경로
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(json_path)
    sav_path = json_path.with_suffix(".sav")

    _backup(sav_path)
    _from_json_to_sav(json_path, sav_path)
    if not sav_path.exists():
        raise RuntimeError("SAV write failed (file not created).")

    print(f"[ok] wrote: {sav_path}")
    return sav_path


if __name__ == "__main__":
    # 예시 실행
    SAVE_DIR = r"C:\Users\PC\AppData\Local\Longvinter\Saved\SaveGames"
    try:
        apply_json_to_sav(SAVE_DIR, "characterStyle-1.0")
        print("SAV 갱신 완료. 게임을 재실행해 적용을 확인하세요.")
    except Exception as e:
        print("[ERROR]", e)
        sys.exit(1)
