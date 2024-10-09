# nlu.py

import spacy
import re
import json
import string

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Define patterns for entity recognition
dish_pattern = re.compile(r'\b(margherita pizza|caesar salad|chocolate lava cake)\b', re.IGNORECASE)
category_pattern = re.compile(r'\b(appetizers?|main courses?|desserts?)\b', re.IGNORECASE)
dietary_pref_pattern = re.compile(r'\b(vegetarian|vegan|gluten[- ]?free)\b', re.IGNORECASE)

# Update intent_patterns
intent_patterns = {
    'greet': re.compile(r'\b(hi|hello|hey)\b', re.IGNORECASE),
    'goodbye': re.compile(r'\b(bye|goodbye|see you)\b', re.IGNORECASE),
    'ask_menu': re.compile(r'\b(menu|have|serve|offer|available)\b', re.IGNORECASE),
    'ask_price': re.compile(r'\b(price|cost|how much)\b', re.IGNORECASE),
    'ask_ingredients': re.compile(r'\b(ingredients|contain|made of|what\'s in)\b', re.IGNORECASE),
    'ask_recommendation': re.compile(r'\b(recommend|suggest|what\'s good|your favorite)\b', re.IGNORECASE),
    'inform': re.compile(r'\b(allergic|don\'t like|prefer|no)\b', re.IGNORECASE),
    'order': re.compile(r'\b(order|get|have|want)\b', re.IGNORECASE),
    'general_ingredients': re.compile(r'\b(dishes with|contains|made with)\b', re.IGNORECASE),
}

# Load menu data
with open('menu.json', 'r') as f:
    MENU_DATA = json.load(f)

    # Extract dish names and categories
dish_names = [item['name'].lower() for item in MENU_DATA]
categories = set(item['category'].lower() for item in MENU_DATA)

# Lemmatize categories
categories_lemma = set([nlp(cat)[0].lemma_ for cat in categories])

# nlu.py (continued)

def extract_entities(message):
    entities = {}
    doc = nlp(message.lower())
    
    # Extract dish names
    for item in MENU_DATA:
        if item['name'].lower() in message.lower():
            entities['dish'] = item['name']
            break
    
    # Extract categories
    for category in categories:
        if category.lower() in message.lower():
            entities['category'] = category
            break
    
    # Extract dietary preferences
    dietary_prefs = ['vegetarian', 'vegan', 'gluten-free']
    for pref in dietary_prefs:
        if pref in message.lower():
            entities['dietary_pref'] = pref
            break
    
    # Extract ingredients
    for token in doc:
        if token.pos_ == 'NOUN' and token.text not in [item['name'].lower() for item in MENU_DATA]:
            entities['ingredient'] = token.text
            break
    
    return entities

def classify_intent(message):
    message = message.lower().translate(str.maketrans('', '', string.punctuation))
    for intent, pattern in intent_patterns.items():
        if pattern.search(message):
            return intent
    return 'unknown'

def nlu(message):
    entities = extract_entities(message)
    intent = classify_intent(message)
    return intent, entities



