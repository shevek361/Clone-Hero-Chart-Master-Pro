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
        self.sliders = {}
        self.setup_ui()

    def setup_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        lang = self.controller.get_lang()

        # Strategie
        s_fr = tk.LabelFrame(self, text=f" {lang['meth']} ", bg="white", padx=15, pady=10)
        s_fr.pack(fill="x", padx=20, pady=10)
        
        self.strat_var = tk.StringVar(value=self.controller.prefs.get("strategy", "Optimale Mischung (Hybrid)"))
        cb = ttk.Combobox(s_fr, textvariable=self.strat_var, values=lang["strat_options"], state="readonly")
        cb.pack(side="left", fill="x", expand=True)
        
        info_s = tk.Label(s_fr, text=" ⓘ ", font=("Arial", 11, "bold"), fg="#3498db", bg="white", cursor="hand2")
        info_s.pack(side="left", padx=5)
        ToolTip(info_s, lang["tt_strat"])

        # Regler
        r_fr = tk.LabelFrame(self, text=f" {lang['prof']} ", bg="white", padx=15, pady=15)
        r_fr.pack(fill="x", padx=20, pady=10)
        
        def_v = self.controller.prefs.get("sliders", {"HardSingle": [50, 4], "MediumSingle": [150, 3], "EasySingle": [400, 2]})
        
        for d in ["HardSingle", "MediumSingle", "EasySingle"]:
            f = tk.Frame(r_fr, bg="white", pady=5); f.pack(fill="x")
            tk.Label(f, text=d, width=15, font=("Arial", 10, "bold"), anchor="w").pack(side="left")
            s = tk.Scale(f, from_=0, to=1000, orient="horizontal", length=300, label=lang["ms_pause"])
            s.set(def_v[d][0]); s.pack(side="left", padx=20)
            fr = tk.Scale(f, from_=0, to=4, orient="horizontal", length=120, label=lang["max_fret"])
            fr.set(def_v[d][1]); fr.pack(side="left")
            
            info_r = tk.Label(f, text=" ⓘ ", font=("Arial", 10), fg="#95a5a6", bg="white", cursor="hand2")
            info_r.pack(side="left", padx=5)
            ToolTip(info_r, lang["tt_slider"])
            self.sliders[d] = (s, fr)

        btn_fr = tk.Frame(self, bg="#f5f6fa", padx=20)
        btn_fr.pack(fill="x", pady=10)
        tk.Button(btn_fr, text=lang["btn_reset"], command=self.reset, bg="#95a5a6", fg="white").pack(side="left")
        tk.Button(btn_fr, text=lang["btn_gen"], command=self.controller.run_gen, 
                  bg="#3498db", fg="white", font=("Arial", 12, "bold"), padx=30, pady=10).pack(side="right")

    def reset(self):
        d = {"HardSingle": [50, 4], "MediumSingle": [150, 3], "EasySingle": [400, 2]}
        for k, v in d.items(): 
            self.sliders[k][0].set(v[0]); self.sliders[k][1].set(v[1])

class LibraryTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        lang = self.controller.get_lang()

        l_fr = tk.LabelFrame(self, text=f" {lang['train']} ", bg="white", padx=15, pady=15)
        l_fr.pack(fill="x", padx=20, pady=20)
        
        self.ent_path = tk.Entry(l_fr, font=("Arial", 10))
        self.ent_path.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(l_fr, text=lang["btn_browse"], command=self.controller.browse).pack(side="left")
        tk.Button(self, text=lang["btn_extract"], command=self.controller.start_learn, 
                  bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), pady=15).pack(pady=10, padx=20, fill="x")
        
        self.lbl_stats = tk.Label(self, text=f"{lang['knowledge']}: {self.controller.proc.db['stats']}", font=("Arial", 11, "italic"))
        self.lbl_stats.pack()
