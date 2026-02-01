CH Chart Master Pro v2.1.0 🎸

CH Chart Master Pro is an AI-supported tool designed to automatically generate lower difficulty levels (Hard, Medium, Easy) for Clone Hero charts. It uses a hybrid approach of Pattern Recognition (from a learned library) and Musical Heuristics to create playable, high-quality charts that feel like they were made by a human.
🌟 Key Features

    Hybrid Intelligence: Combines a database of professional chart patterns with mathematical rules for chord simplification and fret distance.

    Library Builder: "Teach" the tool by feeding it existing professional charts. It learns how experts simplify complex riffs.

    Multi-Language Support: Easily switch between English, German, and Spanish via the UI.

    Real-Time Feedback: Includes a progress bar and a live log ("Blackbox") showing the exact file path currently being processed.

    Safety First: A dedicated "Stop Process" button allows you to cancel long training sessions without closing the application.

🛠 Installation

    Requirement: Ensure you have Python 3.8+ installed.

    Dependencies: Install the required MIDI processing library:
    Bash

    pip install mido

    Files: Place main.py, processor.py, and gui_components.py in the same folder.

    Launch: Run the application via:
    Bash

    python main.py

🚀 How to Use
1. Building your Knowledge Base (Library Builder)

Before generating high-quality charts, the tool needs "knowledge":

    Go to the Library Builder tab.

    Select your Clone Hero "Songs" folder.

    Click Extract Knowledge. The tool will scan all .chart and .mid files and store patterns in chart_library.json.

    The log will show you exactly which artist and song is currently being analyzed.

2. Generating Charts

    Switch to the Generator tab.

    Choose your Method:

        Hybrid: Best of both worlds (DB + Math).

        Pro Charts (DB only): Only uses patterns it has seen before.

        Pure Heuristics: Uses only the sliders and mathematical logic.

    Adjust the Profiles & Intensity sliders to define how "busy" the lower difficulties should be.

    Click Load & Generate, select your Expert-only file, and save the new multi-difficulty chart.

📁 Project Structure
File	Description
main.py	The core application, UI logic, and language management.
processor.py	The "Brain" – handles MIDI/Chart parsing and AI logic.
gui_components.py	UI layout, Sliders, Tabs, and Tooltips.
chart_library.json	The database where learned patterns are stored.
user_settings.json	Stores your language and slider preferences.
