import os
import json
import re
import mido
import random

class SmartProcessor:
    def __init__(self):
        self.lib_file = "chart_library.json"
        self.db = self.load_db()
        self.diff_priority = ["ExpertSingle", "HardSingle", "MediumSingle", "EasySingle"]
        self.tolerance = 10 
        self.last_fret = 0 

    def load_db(self):
        if os.path.exists(self.lib_file):
            try:
                with open(self.lib_file, "r", encoding="utf-8") as f: 
                    db = json.load(f)
                    if "patterns" not in db: db["patterns"] = {}
                    if "learned_files" not in db: db["learned_files"] = []
                    if "stats" not in db: db["stats"] = 0
                    return db
            except: pass
        return {"patterns": {}, "stats": 0, "learned_files": []}

    def save_db(self):
        self.db["learned_files"] = list(set(self.db.get("learned_files", [])))
        with open(self.lib_file, "w", encoding="utf-8") as f: 
            json.dump(self.db, f, indent=4)

    def _get_best_pattern(self, key, diff):
        """Wählt das am häufigsten gelernte Pattern aus der Datenbank."""
        if key in self.db["patterns"] and diff in self.db["patterns"][key]:
            options = self.db["patterns"][key][diff]
            if isinstance(options, dict):
                best_fit = max(options, key=options.get)
                return best_fit.split("_")
            else:
                return options.split("_")
        return None

    def _apply_musical_rules(self, allowed_frets, diff):
        """Mathematische Regeln für die Notenauswahl (Heuristik)."""
        if not allowed_frets: return None
        
        # Akkord-Vereinfachung
        if diff == "EasySingle":
            res = [str(f) for f in allowed_frets[:1]] # Nur Single Notes für Easy
        elif diff == "MediumSingle":
            res = [str(f) for f in allowed_frets[:2]] # Max 2 Noten für Medium
        else:
            res = [str(f) for f in allowed_frets[:3]] # Max 3 Noten für Hard

        # Fret-Distanz Optimierung
        if len(res) == 1 and diff == "EasySingle":
            current = int(res[0])
            if abs(current - self.last_fret) > 2:
                closest = min(allowed_frets, key=lambda x: abs(x - self.last_fret))
                res = [str(closest)]
            self.last_fret = int(res[0])
            
        return res

    def generate(self, path, settings, strategy, midi_track="PART GUITAR"):
        if path.lower().endswith('.mid'):
            all_s, bpm = self.parse_midi(path, midi_track)
            hdr = "[Song]\n{\n  Resolution = 480\n}\n[SyncTrack]\n{\n  0 = TS 4\n  0 = B 120000\n}\n"
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f: raw = f.read()
            all_s, bpm = self.parse_chart(raw); hdr = raw.split("[", 1)[0]
        
        src = next((d for d in self.diff_priority if d in all_s), None)
        if not src: raise ValueError("Keine Quelle gefunden.")
        src_n = self._extract_notes(all_s[src])
        gen, stats = {}, {"lib": 0, "heur": 0, "simplified": 0, "cleaned": 0}
        ms_per_tick = (60000.0 / bpm) / 480 

        for trg in self.diff_priority:
            if trg in all_s or self.diff_priority.index(trg) < self.diff_priority.index(src): continue
            new_n, lt = {}, -999999
            ms_limit = settings[trg]["speed"]
            max_f = settings[trg]["frets"]
            self.last_fret = 0

            for t in sorted(src_n.keys(), key=int):
                curr_t = int(t)
                if (curr_t - lt) * ms_per_tick < ms_limit: continue
                
                f_only = [int(n[0]) for n in src_n[t]]
                key = "_".join(sorted([str(f) for f in f_only]))
                res = None
                
                if strategy in ["Optimale Mischung (Hybrid)", "Optimal Mix (Hybrid)", "Mezcla Óptima (Híbrido)"] or "DB" in strategy:
                    res = self._get_best_pattern(key, trg)
                    if res: stats["lib"] += 1
                
                if not res:
                    allowed = sorted([f for f in f_only if f <= max_f])
                    if len(allowed) > (2 if trg == "EasySingle" else 3):
                        stats["simplified"] += 1
                    res = self._apply_musical_rules(allowed, trg)
                    if res: stats["heur"] += 1
                
                if res:
                    unique_res = sorted(list(set(res)))
                    if len(unique_res) < len(res): stats["cleaned"] += 1
                    new_n[t] = [(f, src_n[t][0][1]) for f in unique_res]
                    lt = curr_t
            gen[trg] = new_n

        out = hdr.strip() + "\n\n"
        for n, lines in all_s.items(): 
            out += f"[{n}]\n{{\n" + "\n".join([f"  {l.strip()}" for l in lines]) + "\n}\n"
        for n, notes in gen.items(): 
            out += f"[{n}]\n{{\n" + "\n".join([f"  {t} = N {f} {l}" for t in sorted(notes.keys(), key=int) for f, l in notes[t]]) + "\n}\n"
        return out, stats

    def learn_from_file(self, path):
        if path in self.db.get("learned_files", []): return "skip"
        try:
            if path.lower().endswith('.mid'): secs, _ = self.parse_midi(path, "PART GUITAR")
            else:
                with open(path, "r", encoding="utf-8", errors="ignore") as f: raw = f.read()
                secs, _ = self.parse_chart(raw)
            avail = [d for d in self.diff_priority if d in secs]
            if len(avail) < 2: return False
            base_n = self._extract_notes(secs[avail[0]])
            for trg in avail[1:]:
                trg_n = self._extract_notes(secs[trg])
                for t_b, data in base_n.items():
                    f_t = next((tx for tx in trg_n.keys() if abs(int(tx)-int(t_b)) <= self.tolerance), None)
                    if f_t:
                        k = "_".join(sorted([n[0] for n in data]))
                        v = "_".join(sorted([n[0] for n in trg_n[f_t]]))
                        if k not in self.db["patterns"]: self.db["patterns"][k] = {}
                        if trg not in self.db["patterns"][k]: self.db["patterns"][k][trg] = {}
                        self.db["patterns"][k][trg][v] = self.db["patterns"][k][trg].get(v, 0) + 1
            self.db["learned_files"].append(path); self.db["stats"] += 1
            return True
        except: return False

    def parse_midi(self, midi_path, target_track_name):
        mid = mido.MidiFile(midi_path)
        sections, bpm = {}, 120
        midi_map = {"ExpertSingle": range(96, 101), "HardSingle": range(84, 89), "MediumSingle": range(72, 77), "EasySingle": range(60, 65)}
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo': bpm = mido.tempo2bpm(msg.tempo)
        for track in mid.tracks:
            if track.name == target_track_name:
                curr_tick = 0
                temp = {d: {} for d in self.diff_priority}
                for msg in track:
                    curr_tick += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        for diff, p_range in midi_map.items():
                            if msg.note in p_range:
                                t = str(curr_tick); f = str(msg.note - p_range.start)
                                if t not in temp[diff]: temp[diff][t] = []
                                temp[diff][t].append((f, "0"))
                for d, notes in temp.items():
                    lines = [f"{t} = N {f} {l}" for t in sorted(notes.keys(), key=int) for f, l in notes[t]]
                    if lines: sections[d] = lines
        return sections, bpm

    def parse_chart(self, content):
        sections, bpm = {}, 120
        sync = re.search(r"\[SyncTrack\]\s*\{([^}]+)\}", content, re.DOTALL)
        if sync:
            m = re.search(r"\d+\s*=\s*B\s*(\d+)", sync.group(1))
            if m: bpm = int(m.group(1)) / 1000
        matches = re.findall(r"\[(\w+)\]\s*\{([^}]+)\}", content, re.DOTALL)
        for name, body in matches: sections[name] = body.strip().split("\n")
        return sections, bpm

    def _extract_notes(self, lines):
        notes = {}
        for l in lines:
            m = re.search(r"(\d+)\s*=\s*N\s*(\d+)\s*(\d+)", l)
            if m:
                t, f, ln = m.groups()
                if t not in notes: notes[t] = []
                notes[t].append((f, ln))
        return notes

    # --- NEU: DIE HIGHWAY-EXTRAKTION ---
    def _extract_all_generated_notes(self, chart_content):
        """Bereitet die Daten für die Highway-Vorschau in der GUI auf."""
        preview_data = {}
        sections = re.findall(r"\[(\w+Single)\]\s*\{([^}]+)\}", chart_content, re.DOTALL)
        for diff_name, body in sections:
            notes_in_diff = {}
            for line in body.strip().split("\n"):
                m = re.search(r"(\d+)\s*=\s*N\s*(\d+)\s*(\d+)", line)
                if m:
                    tick, f, ln = m.groups()
                    if tick not in notes_in_diff: notes_in_diff[tick] = []
                    notes_in_diff[tick].append((f, ln))
            preview_data[diff_name] = notes_in_diff
        return preview_data
