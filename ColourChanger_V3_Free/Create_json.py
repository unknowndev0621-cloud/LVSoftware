# Create_json.py
from pathlib import Path
import subprocess, sys, os

'''
Description:
Function for READING .sav files & CREATING .json files --> Readable (utf-8) 
'''

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
UESAVE = BASE / ("uesave.exe" if os.name == "nt" else "uesave")  
'''
#1) MEIPASS:
When the exe file launches, all resources (.py files) would be loaded in User\PC\AppData\Local\MEIPASS

#2) sys._MEIPASS:
When the files in MEIPASS are working, OBJECT sys make attribute called "_MEIPASS" and it saves the path of MEIPASS

#3) getattr(object name, attribute name, default):
This is a function gathering value of attribute from specific object INCLUDING default value
--> object sys contains _MEIPASS as attribute and its value is the path BUT if the method can't find it, default would be Path(__file__).parent

#4) __file__:
It means the current file running itself
So Path(__file__).parent could be DIR of the file running which can be MEIPASS

'''
def _to_json_text(sav: Path) -> str:
    out = subprocess.check_output([str(UESAVE), "to-json", "--input", str(sav)])
    '''
    #1) subprocess.check_output():
    This is a method for making external program available such as UESAVE
    AND
    This will return ***'BYTES'***

    #2) List [a, b, c, d]: 
    This would be all CLI in cmd 

    #3) parameters:
    a: This would be the path of the program we are trying to use
    b: to-json is the command for UESAVE (change it into json structure)
    c: --input--> so change which one?
    d: the path of sav files location

    '''
    return out.decode("utf-8", errors="replace")

def create_json(path):
    sav_dir = Path(path)
    created = []
    for sav in sav_dir.glob("characterStyle-1.0.sav"):
        jpath = sav.with_suffix(".json")
        '''
        #1) with_suffix():
        Return Path object with extension '.json'
        '''
        jpath.write_text(_to_json_text(sav), encoding="utf-8")
        print("Wrote:", jpath)
        created.append(jpath)
    if not created:
        print("characterStyle-1.0.json is not created")
    return created

