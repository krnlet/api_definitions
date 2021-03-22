# api_definitions
Extract law definitions

To start, you'll need do the next steps:
        1. Clone this repository 
        2. In your terminal write: cd api_definitions
        3. You need a virtual enviroment, 
           (if you don't have, try with: pip install virtualenv), 
           then write: python3 -m venv env
        4. Activate the virtual enviroment: source env/bin/activate
        5. Install the requeriments: pip install -r requirements.txt
        6. Install the spanish spacy (depending to the lenguage):
           python -m spacy download es_core_news_sm
        7. Run the api: FLASK_APP=app.py flask run
        8. Go to http://127.0.0.1:5000 
        
