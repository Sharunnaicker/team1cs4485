# from openai import OpenAI
# import os
# import PyPDF2
# from dotenv import load_dotenv


# load_dotenv()


# api_key = os.getenv("OPENAI_API_KEY")


# client = OpenAI(
#     api_key=api_key,
# )


# def extract_text_from_pdf(pdf_path):
#     """
#     Extract text from a PDF file.
#     """
#     try:
#         with open(pdf_path, 'rb') as file:
#             reader = PyPDF2.PdfReader(file)
#             text = ''
#             for page in reader.pages:
#                 text += page.extract_text()
#         return text
#     except Exception as e:
#         print(f"Error reading PDF file: {e}")
#         return None


# def main():

#     pdf_path = input(
#         "Please enter the path to your restaurant menu PDF file: ")

#     menu_text = extract_text_from_pdf(pdf_path)
#     if menu_text is None:
#         print("Failed to extract text from the PDF. Please check the file and try again.")
#         return

#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 f"You are an AI assistant for a restaurant. Here is the menu:\n{menu_text}\n"
#                 "Help the customer with their order, answer questions about the menu, and take their order. "
#                 "If the customer asks for the total, provide a reasonable total price for the items ordered."
#             )
#         },
#         {"role": "assistant", "content": "Hi, I will take your order."},
#     ]

#     print(">> Hi, I will take your order")

#     while True:
#         user_input = input('>: ')
#         messages.append({"role": "user", "content": user_input})

#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             max_tokens=200,
#             n=1,
#             stop=None,
#             temperature=0.7,
#         )

#         assistant_reply = response.choices[0].message.content

#         print(f">> {assistant_reply}")

#         messages.append({"role": "assistant", "content": assistant_reply})

#         if any(phrase in assistant_reply.lower() for phrase in ['proceed to checkout', 'your total is', 'have a nice day', 'thank you']):
#             break


# if __name__ == "__main__":
#     main()



# chatbot.py

import json
from nlu import nlu
import spacy

nlp = spacy.load('en_core_web_sm')

# Load menu data
with open('menu.json', 'r') as f:
    MENU_DATA = json.load(f)


# chatbot.py (continued)

def get_menu_items(category=None, dietary_pref=None):
    items = MENU_DATA
    if category:
        category_lemma = nlp(category.lower())[0].lemma_
        items = [item for item in items if nlp(item['category'].lower())[0].lemma_ == category_lemma]
    if dietary_pref:
        items = [item for item in items if dietary_pref.lower() in [d.lower() for d in item['dietary_info']]]
    return items


def handle_greet(entities):
    return "Hello! Welcome to our restaurant. How can I assist you today?"

def handle_goodbye(entities):
    return "Thank you for visiting. Have a great day!"

def handle_ask_menu(entities):
    category = entities.get('category')
    dietary_pref = entities.get('dietary_pref')
    items = get_menu_items(category, dietary_pref)
    
    if items:
        item_names = ', '.join([item['name'] for item in items])
        return f"Here are the items{f' in {category}' if category else ''}{f' that are {dietary_pref}' if dietary_pref else ''}: {item_names}."
    else:
        return "I'm sorry, we don't have any items matching your request."

def handle_ask_price(entities):
    dish = entities.get('dish')
    if dish:
        for item in MENU_DATA:
            if item['name'].lower() == dish.lower():
                return f"The price of {item['name']} is ${item['price']:.2f}."
        return f"Sorry, {dish} is not on our menu."
    else:
        return "Please specify the dish you are interested in."

def handle_ask_ingredients(entities):
    dish = entities.get('dish')
    if dish:
        for item in MENU_DATA:
            if item['name'].lower() == dish.lower():
                ingredients = ', '.join(item['ingredients'])
                return f"The ingredients in {item['name']} are: {ingredients}."
        return f"I'm sorry, but I couldn't find {dish} on our menu. Can I help you with another dish?"
    else:
        return "Which dish would you like to know the ingredients for?"

def handle_ask_recommendation(entities):
    dietary_pref = entities.get('dietary_pref')
    category = entities.get('category')
    items = get_menu_items(category, dietary_pref)
    
    if items:
        recommendation = items[0]['name']
        return f"I recommend trying our {recommendation}."
    else:
        return "I'm sorry, I don't have any recommendations based on your preferences."

def handle_inform(entities):
    return "Thank you for letting me know. How can I assist you further?"

def handle_unknown(entities):
    return "I'm sorry, I didn't understand that. Could you please rephrase?"


# chatbot.py (continued)

intent_handlers = {
    'greet': handle_greet,
    'goodbye': handle_goodbye,
    'ask_menu': handle_ask_menu,
    'ask_price': handle_ask_price,
    'ask_ingredients': handle_ask_ingredients,
    'ask_recommendation': handle_ask_recommendation,
    'inform': handle_inform,
    'unknown': handle_unknown,
}


# chatbot.py (continued)

def get_response(message):
    intent, entities = nlu(message)
    response_func = intent_handlers.get(intent, handle_unknown)
    response = response_func(entities)
    return response


# chatbot.py (continued)

def main():
    print("Bot: Hello! Welcome to our restaurant. How can I assist you today?")
    order = []
    while True:
        message = input("You: ")
        if message.lower() in ['exit', 'quit', 'goodbye', 'bye']:
            if order:
                total = sum(item['price'] for item in order)
                print(f"Bot: Your order includes: {', '.join([item['name'] for item in order])}. The total is ${total:.2f}.")
            print("Bot:", handle_goodbye({}))
            break
        
        intent, entities = nlu(message)
        
        if intent == 'order':
            dish = entities.get('dish')
            if dish:
                for item in MENU_DATA:
                    if item['name'].lower() == dish.lower():
                        order.append(item)
                        break
        
        response = get_response(message)
        print("Bot:", response)
        
        if order and "Would you like anything else?" not in response:
            print(f"Bot: Your current order includes: {', '.join([item['name'] for item in order])}.")

if __name__ == "__main__":
    main()
