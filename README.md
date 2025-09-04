# anki-flashcards-creator
Application uses ANKI API client to create new flashcards on Anki web and make user available to create easily flashcards using list of words from a file.

To generate new notes, user has to follow below steps:
1. copy content of [.env.example](./.env.example) file to `.env` file and fill with adequate content in the variables
2. run command prompt
3. create a new virtual environment<br>
`python -m venv venv`
4. activate virtual environment<br>
`"./venv/Scripts/activate"` - for windows
5. install all dependencies<br>
`pip install -r requirements.txt`
6. activate script<br>
`python anki_note_gen.py`

Script requires to parse to XLSX file with words. Script requires 3 columns to be read from Excel file. By default their names are:<br>
<li> <b>word</b> - word name in english
<li> <b>definition</b> - meaning of a word in polish
<li> <b>example</b> - example of a use of a word

User has to also have a predefined `deck` and `card model`. 

Deck name is predefined in [constants.py](./constants.py) in a variable `CURR_LANG`. By default it is **English**

Model name is defined in [constants.py](./constants.py) in a variable `MODEL_NAME`. By default it is: **Słownictwo z odwrotną kartą i multimediami**

If user doesn't know which parameters have to be in a card model, it is also presented below:
<li> <b>Słowo PL</b> - word in polish
<li> <b>FrontAudio</b> - audio with pronounciation of a word in english (at the front of a card)
<li> <b>Słowo EN</b> - word in english
<li> <b>BackAudio</b> - audio with pronounciation of a word in english (at the back of a card)
<li> <b>Obrazek</b> - image of a word
<li> <b>Audio</b> - audio with pronounciation of a word
<li> <b>Przykład EN</b> - example of a use of a word in english

Above parameters are also defined in [constants.py](./constants.py) in a variable `FIELDS` values. This is the place where it can be changed.
