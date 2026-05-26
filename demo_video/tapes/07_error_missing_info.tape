# Query 7: Error case - information not in source documents
# Highlights: system explicitly states when info is unavailable (no hallucination)

Output recordings/07_error_missing_info.mp4

Set Shell bash
Set FontSize 18
Set Width 1400
Set Height 800
Set Theme "Dracula"
Set TypingSpeed 40ms
Set PlaybackSpeed 1.0

Hide
Type "cd /home/axel-oeberg/pvk/quantera && source venv/bin/activate && clear"
Enter
Sleep 500ms
Show

Sleep 800ms
Type `make query Q="What is the CEO compensation of Volvo Group in Q1 2025?"`
Sleep 500ms
Enter
Sleep 15s
