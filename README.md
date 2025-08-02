# anki-flashcards-creator
Application uses ANKI API client to create new flashcards on Anki web and make user available to create easily flashcards using list of words from a file.

To generate new notes, user has to follow below steps:
1. copy content of [.env.example](./.env.example) file to `.env` file and fill with adequate content
2. create a new virtual environment<br>
`python -m venv venv`
3. activate virtual environment<br>
`"./venv/Scripts/activate"` - for windows
4. install all dependencies<br>
`pip install -r requirements.txt`
5. activate script<br>
`python <filepath.csv> anki_note_gen.py`