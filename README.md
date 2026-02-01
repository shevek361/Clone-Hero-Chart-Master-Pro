==========================================================
🎸 CH CHART MASTER PRO v1.9.6 - Kurzanleitung
==========================================================

Dieses Tool hilft dir dabei, für deine Clone Hero Expert-Charts 
automatisch die Schwierigkeitsgrade Hard, Medium und Easy zu 
erstellen ("Downcharting").

----------------------------------------------------------
1. VORBEREITUNG
----------------------------------------------------------
Damit das Programm startet, muss Python installiert sein.
Zudem wird die Bibliothek 'mido' benötigt.
Öffne deine Kommandozeile (CMD) und gib ein:

pip install mido

----------------------------------------------------------
2. DIE REITER (TABS)
----------------------------------------------------------

A) 🚀 GENERATOR
Hier erstellst du deine Charts. 
1. Wähle eine Strategie (siehe unten).
2. Lade eine .chart oder .mid Datei.
3. Das Tool berechnet die Noten und fragt dich nach dem Speicherort.

B) 📚 LIBRARY BUILDER
Hier "fütterst" du das Wissen des Tools.
Wähle einen Ordner mit fertigen, guten Songs aus (z.B. Rock Band Exporte).
Das Tool lernt die Abfolgen der Profis und speichert sie in der 
Datei 'chart_library.json'. Je mehr Songs du einliest, desto 
besser werden deine Ergebnisse!

----------------------------------------------------------
3. DIE STRATEGIEN (Welche soll ich wählen?)
----------------------------------------------------------

- Optimale Mischung (Hybrid): 
  Das Tool schaut zuerst in sein gelerntes Wissen. Findet es nichts, 
  rechnet es mathematisch nach. (Beste Wahl für fast alles!)

- Profi-Charts (Nur DB): 
  Nutzt NUR das Wissen aus deiner Datenbank. Klingt sehr menschlich, 
  kann aber Lücken lassen, wenn das Tool ein Pattern noch nicht kennt.

- Reine Heuristik (Mathematisch): 
  Ignoriert das Wissen und rechnet starr nach deinen Regler-Einstellungen. 
  Gut für sehr gleichmäßige, technische Charts.

----------------------------------------------------------
4. TIPPS & TRICKS
----------------------------------------------------------
- INFO-BUTTONS: Neben den Reglern findest du kleine "i"-Symbole. 
  Fahre mit der Maus darüber, um eine kurze Erklärung zur Funktion 
  zu erhalten.
  
- STOPP-TASTE: Wenn du einen riesigen Ordner analysierst und es 
  zu lange dauert, kannst du den Vorgang jederzeit sicher abbrechen.

- MIDI-DATEIEN: Wenn du eine .mid lädst, fragt dich das Tool, welche 
  Spur (z.B. PART GUITAR) genutzt werden soll.

----------------------------------------------------------
5. PROGRAMM STARTEN (LINUX)
----------------------------------------------------------
Du kannst das Programm bequem über die 'start_chartmaster.sh' starten.
1. Rechtsklick auf die Datei -> Eigenschaften -> Berechtigungen.
2. "Datei als Programm ausführen" aktivieren.
3. Doppelklick auf die Datei.

Alternativ im Terminal:
chmod +x start_chartmaster.sh
./start_chartmaster.sh

----------------------------------------------------------
6. WINDOWS EXE VERSION
----------------------------------------------------------
Wenn du eine 'chart_master.exe' hast, benötigst du KEIN Python. 
Einfach die EXE starten. Die 'chart_library.json' muss im selben 
Ordner liegen wie die EXE, damit dein Wissen geladen wird.

Viel Spaß beim Charten!
