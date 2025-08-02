# anki-flashcards-creator
Application uses ANKI API client to create new flashcards on Anki web and make user available to create easily flashcards using list of words from a file.

To generate new notes, user has to follow below steps:

1. create a new virtual environment<br>
`python -m venv venv`
2. activate virtual environment<br>
`"./venv/Scripts/activate"` - for windows
3. install all dependencies<br>
`pip install -r requirements.txt`
4. activate script<br>
`python <filepath.csv> anki_note_gen.py`