# Create_json.py
from pathlib import Path
import subprocess, sys, os
from datetime import datetime

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
UESAVE = BASE / ("uesave.exe" if os.name == "nt" else "uesave")  

def _to_json_text(sav: Path) -> str:
    out = subprocess.check_output([str(UESAVE), "to-json", "--input", str(sav)])
    return out.decode("utf-8", errors="replace")

def create_json(path):
    """
    path: SaveGames 디렉터리
    *.sav -> 같은 이름의 .json 생성/갱신
    """
    sav_dir = Path(path)
    created = []
    for sav in sav_dir.glob("characterStyle-1.0.sav"):
        jpath = sav.with_suffix(".json")
        jpath.write_text(_to_json_text(sav), encoding="utf-8")
        print("Wrote:", jpath)
        created.append(jpath)
    if not created:
        print("characterStyle-1.0.json is not created")
    return created

