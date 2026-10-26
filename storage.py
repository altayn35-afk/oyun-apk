"""Atomic local player data, including persistent shared lives."""
import json
import os
import time
from pathlib import Path
GAMES = ("balon", "ari", "sekil", "bulmaca")
class SaveStore:
    def __init__(self, directory):
        self.path = Path(directory) / "player.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = {"name":"", "sound":True, "music":True, "lives":3, "next_life_at":None,
            "games":{g:{"best":0,"level":0,"completed":0,"stars":0} for g in GAMES}}
        try:
            raw=json.loads(self.path.read_text(encoding="utf8"))
            if isinstance(raw.get("name"),str): self.data["name"]=raw["name"][:20]
            for k in ("sound","music"):
                if isinstance(raw.get(k),bool): self.data[k]=raw[k]
            if type(raw.get("lives")) is int and 0<=raw["lives"]<=3:
                self.data["lives"]=raw["lives"]
            t=raw.get("next_life_at")
            if type(t) in (float,int) and 0<t<1e12:
                self.data["next_life_at"]=float(t)
            for g in GAMES:
                for k in self.data["games"][g]:
                    v=raw.get("games",{}).get(g,{}).get(k,0)
                    if type(v) is int and v>=0: self.data["games"][g][k]=v
        except (OSError,ValueError,TypeError,AttributeError):
            try: self.data["name"]=(self.path.parent/"isim.txt").read_text(encoding="utf8").strip()[:20]
            except OSError: pass
    def save(self):
        tmp=self.path.with_suffix(".tmp")
        with tmp.open("w",encoding="utf8") as f:
            json.dump(self.data,f,ensure_ascii=False)
            f.flush();os.fsync(f.fileno())
        os.replace(tmp,self.path)
    def record(self,game,score,level=0,completed=False,stars=0):
        d=self.data["games"][game]
        d["best"]=max(d["best"],score)
        d["level"]=max(d["level"],level)
        if completed: d["completed"]+=1;d["stars"]+=stars
        self.save()
