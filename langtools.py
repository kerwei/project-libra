import os

from collections import defaultdict
from itertools import chain, product
from nltk.corpus import wordnet as wn
from nltk.tag.perceptron import PerceptronTagger


# A simple selection of genre
CATEGORIES = [
    'adventure', 
    'war', 
    'hobbies',
    'fantasy',
    'humor', 
    'mystery', 
    'romance', 
    'science'
]
# Default POS tagger
TAGGER = PerceptronTagger()


class Genre:
    """
    Each genre object has 3 attributes:
        synsets: same-level synonyms
        hypernyms: the parent lexical of a genre
        hypoynyms: the children lexical of a genre
    These attributes will be used to attempt the recognition of the genre of a book
    """
    def __init__(self, word):
        self.synsets = set(wn.synsets(word))
        self.name_synsets = list(set([wd.name() for wd in self.synsets]))

        self.hypernyms = list(set([hype for ns in self.name_synsets for hype in wn.synset(ns).hypernyms()]))
        self.hyponyms = list(set([hypo for ns in self.name_synsets for hypo in wn.synset(ns).hyponyms()]))

    @property
    def flat_attrib(self):
        """
        All related synsets in a single flat set
        """
        return set([syn for lst in self.attrib.values() for syn in lst])

    @property
    def attrib(self):
        """
        Synset object dictionary of all attributes
        """
        return {
            'synsets': self.synsets,
            'hypernyms': self.hypernyms,
            'hyponyms': self.hyponyms
        }


def create_all_genre():
    """
    Build the collection of genre and pickle the object
    """
    genre_all = {i: Genre(i) for i in CATEGORIES}

    return genre_all


# Resources
GENRE = create_all_genre()


def extract_featureset(title):
    """
    Extract the features - verbs and nouns of a title
    """
    features = {}
    features['noun'] = [(word.lower(), 'n') for word, tag in TAGGER.tag(title.split()) if 'NN' in tag]
    features['verb'] = [(word.lower(), 'v') for word, tag in TAGGER.tag(title.split()) if 'VB' in tag]

    return features


def assign_genre(featureset):
    """
    Attempts to score the features to determine an appropriate genre
    Returns a dictionary of genre with respective scores
    """
    # Flatten the featureset
    flatten_features = set(tpl for lst in featureset.values() for tpl in lst)
    features_synset = {wn.synsets(word, pos)[0] for word, pos in flatten_features if wn.synsets(word, pos)}

    # Init scoreboard
    scoreboard = defaultdict(int)
    for genre, gobj in GENRE.items():
        # If there are common synsets between the genre and feature, apply the genre
        if features_synset.intersection(gobj.flat_attrib):
            scoreboard[genre] = 1
            continue

        # Otherwise, calculate the max path_similarity score between each feature and each synset of the genre
        maxscore = float('-inf')
        for feat, gattrib in product(features_synset, gobj.flat_attrib):
            # Path_similarity has no return value when comparing different POS (possibly)
            score = feat.path_similarity(gattrib)
    
            if score:
                maxscore = max([maxscore, score])

        scoreboard[genre] = maxscore

    return scoreboard
