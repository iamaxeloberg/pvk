# Query 6: Error case - company not in portfolio
# Highlights: graceful "no documents found" handling

Output recordings/06_error_unknown_company.mp4

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
Type `make query Q="What is the Q1 2025 revenue of Tesla?"`
Sleep 500ms
Enter
Sleep 10s
