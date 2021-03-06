# Simple Book Catalogue

## Overview
This application keeps a list of books, their respective authors and genres. From the browser interface, users are able to add a new book, as well as deleting an existing book from the database. Upon the addition of a book, the linguistic service within the application will attempt to guess the genre that the book belongs to. If genres can be successfully "guessed", the book will then be displayed in the top 10 latest books table, located below the form. If the service cannot ascertain the genre of the book, the entry will not be displayed, but will still exist in the database.

## Automatic genre assignment methodology
The only input required by the linguistic service is the title of the book. The engine then goes through the following steps to try to determine the genre:
1. Perform a part of speech tagging on the title
2. Extract the features required for identifying the genre. This is currently set to nouns and verbs.
3. The synonyms of the features are generated by the wordnet package from the nltk module. In addition, the hypernyms and hyponyms of each synset are also generated and collectively, these form the full set of sense attributes for each of the feature extracted from the title.
4. The same steps of generating synsets, hypernyms and hyponyms are also performed on a pre-defined set of genres to produce the set of sense attributes that the features need to be cross-referenced against.
5. To ascertain the likeliness of a genre being relevant to the features in the title, the path_similarity function from the wordnet package is used. The function generates a score for a pair of synsets, to denote how similar they are based on the shortest path that connects the pair within the lexical taxonomy.
6. Finally, a genre is deemed to be relevant if the maximum of the path_similarity score found from the pool of cross-referenced attributes is greater than the preset threshold.

## Machine setup
The application has been deployed onto a Lightsail instance at http://54.179.151.212:5000/
Specifications of the instance is given below:
- Ubuntu 18.04.1 LTS
- 512 MB RAM
- 1 vCPU

### Software requirements
- Python 3.7 (please see requirements.txt for all required modules)
- PostgreSQL 11

## Installation
### Database
1. The installation guide assumes that postgresql is already installed and running on the server while listening on its default ports. The remaining steps will focus on the additional set up that is required by the application.
2. Connect to postgresql at the default database as the default user.
```
psql -d postgres -U postgres
```
3. Enter each of the following commands in sequence to create a new databse and a new user to be used by the application:
```sql
CREATE USER libra WITH PASSWORD 'passw0rd';
CREATE DATABASE catalogue;
GRANT CONNECT ON DATABASE catalogue TO libra;
GRANT ALL PRIVILEGES ON DATABASE catalogue TO libra;
```

### Application
1. The installation guide assumes that the machine has Python 3+ already installed. It is also highly recommended that the application be run from a virtual environment.
2. Change directory into the root project folder and install all required python packages. Note that nltk data packages need to be installed separately, **AFTER** the nltk module installation is complete
```
pip install -r requirements.txt
python -c 'import nltk; nltk.download("wordnet")'
```
3. Firstly, create all the application data models
```
python database_setup.py
```
4. _OPTIONAL_ Load the database with mock data
```
python loaddata.py
```
5. Start the api service application. The api service runs as a web service and listens on the localhost at port 2020
```
python appapiservice.py
```
6. Finally, from a separate process, start the web application. It is set to listen on all public IPs at port 5000
```
python main.py
```






