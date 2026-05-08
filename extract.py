import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv(override=True) 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Setup Groq Brain
client = Groq(api_key=GROQ_API_KEY)

# Helper function to turn the image into code so Groq can "see" it
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_receipt(image_path):
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        return f"Error opening image: {e}"

    prompt = """
    Extract the following data from this receipt image. 
    It might be handwritten or messy. Do your best to read the cursive.
    If a field is truly missing (like there is no date), use "Unknown".
    
    Return ONLY a raw JSON object with these keys exactly: merchant_name, date, total_amount, currency, category.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct", # The new Vision Brain!
            temperature=0, 
            response_format={"type": "json_object"} 
        )

        result_text = chat_completion.choices[0].message.content
        return json.loads(result_text)
        
    except Exception as e:
        return f"Error talking to Groq: {e}"