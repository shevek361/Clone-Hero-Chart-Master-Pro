import tkinter as tk
from tkinter import ttk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify='left', background="#ffffe0", 
                 relief='solid', borderwidth=1, font=("tahoma", "9", "normal"), 
                 padx=5, pady=5).pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class GeneratorTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        
        # Strategie Auswahl
        s_fr = tk.LabelFrame(self, text=" Methode ", bg="white", padx=15, pady=10)
        s_fr.pack(fill="x", padx=20, pady=10)
        
        self.strat_var = tk.StringVar(value=controller.prefs.get("strategy", "Optimale Mischung (Hybrid)"))
        cb = ttk.Combobox(s_fr, textvariable=self.strat_var, 
                          values=["Optimale Mischung (Hybrid)", "Profi-Charts (Nur DB)", "Reine Heuristik (Mathematisch)"], 
                          state="readonly")
        cb.pack(side="left", fill="x", expand=True)
        
        info_s = tk.Label(s_fr, text=" ⓘ ", font=("Arial", 11, "bold"), fg="#3498db", bg="white", cursor="hand2")
        info_s.pack(side="left", padx=5)
        ToolTip(info_s, "HYBRID: Nutzt Profi-Patterns wenn möglich.\nNUR DB: Nur bekannte Patterns.\nMATHEMATIK: Nur Regler-basiert.")

        # Regler
        self.sliders = {}
        r_fr = tk.LabelFrame(self, text=" Profile & Intensität ", bg="white", padx=15, pady=15)
        r_fr.pack(fill="x", padx=20, pady=10)
        
        def_v = controller.prefs.get("sliders", {"HardSingle": [50, 4], "MediumSingle": [150, 3], "EasySingle": [400, 2]})
        
        for d in ["HardSingle", "MediumSingle", "EasySingle"]:
            f = tk.Frame(r_fr, bg="white", pady=5); f.pack(fill="x")
            tk.Label(f, text=d, width=15, font=("Arial", 10, "bold"), anchor="w").pack(side="left")
            
            s = tk.Scale(f, from_=0, to=1000, orient="horizontal", length=300, label="ms Pause")
            s.set(def_v[d][0]); s.pack(side="left", padx=20)
            
            fr = tk.Scale(f, from_=0, to=4, orient="horizontal", length=120, label="Max Fret")
            fr.set(def_v[d][1]); fr.pack(side="left")
            
            # Hier sind die Tooltips zurück:
            info_r = tk.Label(f, text=" ⓘ ", font=("Arial", 10), fg="#95a5a6", bg="white", cursor="hand2")
            info_r.pack(side="left", padx=5)
            ToolTip(info_r, f"ms Pause: Mindestabstand zwischen Noten.\nMax Fret: Höchste erlaubte Taste (0=Grün, 4=Orange).")
            
            self.sliders[d] = (s, fr)

        btn_fr = tk.Frame(self, bg="#f5f6fa", padx=20)
        btn_fr.pack(fill="x", pady=10)
        tk.Button(btn_fr, text="WERTE ZURÜCKSETZEN", command=self.reset, bg="#95a5a6", fg="white").pack(side="left")
        tk.Button(btn_fr, text="LADEN & GENERIEREN", command=controller.run_gen, 
                  bg="#3498db", fg="white", font=("Arial", 12, "bold"), padx=30, pady=10).pack(side="right")

    def reset(self):
        d = {"HardSingle": [50, 4], "MediumSingle": [150, 3], "EasySingle": [400, 2]}
        for k, v in d.items(): 
            self.sliders[k][0].set(v[0])
            self.sliders[k][1].set(v[1])

class LibraryTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        l_fr = tk.LabelFrame(self, text=" Training ", bg="white", padx=15, pady=15)
        l_fr.pack(fill="x", padx=20, pady=20)
        
        self.ent_path = tk.Entry(l_fr, font=("Arial", 10))
        self.ent_path.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(l_fr, text="Ordner...", command=controller.browse).pack(side="left")
        tk.Button(self, text="📚 Wissen extrahieren", command=controller.start_learn, 
                  bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), pady=15).pack(pady=10)
        
        self.lbl_stats = tk.Label(self, text=f"Wissen: {controller.proc.db['stats']} Songs", font=("Arial", 11, "italic"))
        self.lbl_stats.pack()
