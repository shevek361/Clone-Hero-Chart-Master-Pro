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
        tk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1, padx=5, pady=5, font=("Arial", 9)).pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class GeneratorTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f6fa")
        self.controller = controller
        self.sliders = {}
        # Die Variable wird hier einmalig zentral definiert
        initial_strat = self.controller.prefs.get("strategy", "")
        self.strat_var = tk.StringVar(value=initial_strat)
        self.zoom_level = 1.0
        self.setup_ui()

    def setup_ui(self):
        # Wir merken uns den Index der aktuellen Auswahl, um ihn nach dem Neuzeichnen wiederherzustellen
        lang = self.controller.get_lang()
        current_val = self.strat_var.get()
        
        # Falls die Variable leer ist, nehmen wir den ersten Standardwert der Sprache
        if not current_val and lang["strat_options"]:
            self.strat_var.set(lang["strat_options"][0])

        for widget in self.winfo_children(): 
            widget.destroy()

        left_pnl = tk.Frame(self, bg="#f5f6fa", width=260)
        left_pnl.pack(side="left", fill="y", padx=10, pady=5)
        left_pnl.pack_propagate(False)

        # Strategie-Bereich
        s_fr = tk.LabelFrame(left_pnl, text=f" {lang['meth']} ", bg="white", padx=10, pady=5)
        s_fr.pack(fill="x", pady=5)
        
        # Combobox nutzt die persistente strat_var
        strat_menu = ttk.Combobox(s_fr, textvariable=self.strat_var, values=lang["strat_options"], state="readonly")
        strat_menu.pack(fill="x")

        # Slider-Bereich
        p_fr = tk.LabelFrame(left_pnl, text=" Intensity & Frets ", bg="white", padx=10, pady=5)
        p_fr.pack(fill="x", pady=5)
        
        saved_sl = self.controller.prefs.get("sliders", {"HardSingle": [50, 4], "MediumSingle": [150, 3], "EasySingle": [400, 2]})

        for diff in ["HardSingle", "MediumSingle", "EasySingle"]:
            row = tk.Frame(p_fr, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=diff, bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
            
            # Bestehende Werte beibehalten oder aus Prefs laden
            curr_s = self.sliders[diff][0].get() if diff in self.sliders else saved_sl.get(diff, [100, 4])[0]
            curr_f = self.sliders[diff][1].get() if diff in self.sliders else saved_sl.get(diff, [100, 4])[1]
            
            s_val = tk.IntVar(value=curr_s)
            tk.Scale(row, from_=0, to=500, orient="horizontal", variable=s_val, bg="white", width=10).pack(fill="x")
            
            f_val = tk.IntVar(value=curr_f)
            tk.Scale(row, from_=0, to=4, orient="horizontal", variable=f_val, bg="white", width=10, label="Max Fret").pack(fill="x")
            self.sliders[diff] = (s_val, f_val)

        # Buttons
        btn_fr = tk.Frame(left_pnl, bg="#f5f6fa")
        btn_fr.pack(side="bottom", fill="x", pady=5)
        tk.Button(btn_fr, text=lang["btn_gen"], command=self.controller.run_gen, bg="#3498db", fg="white", font=("Arial", 10, "bold"), pady=8).pack(fill="x")
        tk.Button(btn_fr, text=lang["btn_reset"], command=self.reset_sliders, font=("Arial", 8)).pack(fill="x", pady=2)

        # Rechter Bereich (Vorschau)
        right_pnl = tk.Frame(self, bg="#1e272e")
        right_pnl.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        h_ctrl = tk.Frame(right_pnl, bg="#2c3e50")
        h_ctrl.pack(fill="x")
        
        self.preview_diff = tk.StringVar(value="HardSingle")
        p_menu = ttk.Combobox(h_ctrl, textvariable=self.preview_diff, values=["ExpertSingle", "HardSingle", "MediumSingle", "EasySingle"], state="readonly", width=15)
        p_menu.pack(side="left", padx=10, pady=5)
        p_menu.bind("<<ComboboxSelected>>", lambda e: self.controller.update_preview())
        tk.Label(h_ctrl, text="Zoom: Ctrl + Wheel", fg="#bdc3c7", bg="#2c3e50", font=("Arial", 8)).pack(side="right", padx=10)

        self.canv_frame = tk.Frame(right_pnl, bg="black")
        self.canv_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.canv_frame, bg="black", highlightthickness=0)
        self.v_scroll = tk.Scrollbar(self.canv_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_zoom)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_zoom(self, event):
        if event.delta > 0: self.zoom_level *= 1.1
        else: self.zoom_level *= 0.9
        self.zoom_level = max(0.1, min(self.zoom_level, 5.0))
        self.controller.update_preview()

    def reset_sliders(self):
        d = {"HardSingle": [50, 4], "MediumSingle": [150, 3], "EasySingle": [400, 2]}
        for k, v in d.items():
            if k in self.sliders: 
                self.sliders[k][0].set(v[0])
                self.sliders[k][1].set(v[1])

class LibraryTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        lang = self.controller.get_lang()
        l_fr = tk.LabelFrame(self, text=f" {lang['train']} ", bg="white", padx=15, pady=10)
        l_fr.pack(fill="x", padx=20, pady=10)
        self.ent_path = tk.Entry(l_fr)
        self.ent_path.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(l_fr, text=lang["btn_browse"], command=self.controller.browse).pack(side="left")
        tk.Button(self, text=lang["btn_extract"], command=self.controller.start_learn, bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), pady=8).pack(pady=10, padx=20, fill="x")
        self.lbl_stats = tk.Label(self, text=f"{lang['knowledge']}: 0", bg="white")
        self.lbl_stats.pack()
