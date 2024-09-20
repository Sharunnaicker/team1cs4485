from openai import OpenAI
import os
import PyPDF2
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(
    api_key=api_key,
)


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None


def main():

    pdf_path = input(
        "Please enter the path to your restaurant menu PDF file: ")

    menu_text = extract_text_from_pdf(pdf_path)
    if menu_text is None:
        print("Failed to extract text from the PDF. Please check the file and try again.")
        return

    messages = [
        {
            "role": "system",
            "content": (
                f"You are an AI assistant for a restaurant. Here is the menu:\n{menu_text}\n"
                "Help the customer with their order, answer questions about the menu, and take their order. "
                "If the customer asks for the total, provide a reasonable total price for the items ordered."
            )
        },
        {"role": "assistant", "content": "Hi, I will take your order."},
    ]

    print(">> Hi, I will take your order")

    while True:
        user_input = input('>: ')
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7,
        )

        assistant_reply = response.choices[0].message.content

        print(f">> {assistant_reply}")

        messages.append({"role": "assistant", "content": assistant_reply})

        if any(phrase in assistant_reply.lower() for phrase in ['proceed to checkout', 'your total is', 'have a nice day', 'thank you']):
            break


if __name__ == "__main__":
    main()
