# import os
# import base64
# from groq import Groq
# import pytesseract
# from PIL import Image
# import json
# from dotenv import load_dotenv

import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
# 1. Figure out EXACTLY where we are on the computer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# 2. Force it to load that exact file
loaded_successfully = load_dotenv(ENV_PATH, override=True)

# 3. Print out what happened to the terminal so we can see it!
print("\n--- SECRETS DEBUG MODE ---")
print(f"Looking for .env at: {ENV_PATH}")
print(f"Did it find the .env file? {loaded_successfully}")



# 1. PASTE  GROQ KEY HERE
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    print(f"Did it find the Groq Key? YES (Length: {len(GROQ_API_KEY)})")
else:
    print("Did it find the Groq Key? NO - It is returning None")
print("--------------------------\n")

# 2. Get the TESSERACT PATH 
path_to_tesseract = os.getenv("TESSERACT_PATH")
# ---------------------

# Setup Tesseract
pytesseract.pytesseract.tesseract_cmd = path_to_tesseract

# Setup Groq Brain
client = Groq(api_key=GROQ_API_KEY)

def process_receipt(image_path):
    print(f" Reading {image_path}...")
    
    # Step A: Get Raw Text (The Eyes)
    try:
        image = Image.open(image_path)
        raw_text = pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error reading image: {e}"

    print("🧠 Thinking (sending to Groq/Llama)...")

    # Step B: Analyze Text (The Brain)
    try:
        prompt = f"""
        Extract the following data from this receipt text:
        {raw_text}
        
        Return ONLY a raw JSON object with these keys exactly: merchant_name, date, total_amount, currency, category.
        """

        # We use Meta's Llama model hosted on Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction assistant. You output pure JSON only."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct", # Super fast, smart model
            temperature=0, # 0 means be strictly factual, not creative
            response_format={"type": "json_object"} # Forces it to return perfect JSON!
        )

        # Step C: Parse the answer
        result_text = chat_completion.choices[0].message.content
        return json.loads(result_text)
        
    except Exception as e:
        return f"Error talking to Groq: {e}"

# RUN IT
if __name__ == "__main__":
    data = process_receipt("receipt.jpg")
    
    # Check if we got an error message (string) or real data (dictionary)
    if isinstance(data, str):
        print(f"\n❌ FAILURE: {data}")
    else:
        print("\n--- 🎯 FINAL DATA (Powered by Groq/Llama) ---")
        try:
            print(f"Store:    {data.get('merchant_name', 'Unknown')}")
            print(f"Date:     {data.get('date', 'Unknown')}")
            print(f"Amount:   {data.get('currency', '$')}{data.get('total_amount', 0)}")
            print(f"Category: {data.get('category', 'Uncategorized')}")
        except Exception as e:
            print(f"Data display error: {e}")