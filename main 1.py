import pytesseract
from pdf2image import convert_from_path
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import cv2
import numpy as np

# Load environment variable from .env file
load_dotenv()

# Get the PDF directory from the environment variable
pdf_directory = os.getenv("PDF_DIRECTORY", os.getcwd())

# This follows the latest convention to interact with prompts with OpenAI, now you have to establish a client.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Helper function to preprocess the image before performing OCR
def preprocess_image(image):

    # Convert to numpy array (since the images from pdf2image are PIL images)
    image_array = np.array(image)

    # This essentially increases the contrast between dark and white, making the text stand out more clearly
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)  # Convert to greyscale first
    # Even if the PDF documents look to be already in greyscale, they are probably still in an RGB format, which could confuse the OCR. 
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoising - this reduces background noise (TV static look), common in scanned document
    denoised = cv2.medianBlur(thresh, 3)

    return denoised

# Helper function to perform OCR on a PDF and extract text from images
def extract_text_from_pdf(pdf_path):
    """
    This function takes a path to a PDF file, converts each page to an image,
    preprocesses the image, and uses OCR to extract text from these images.
    """
    # Convert PDF pages to images (300 DPI for good quality)
    pages = convert_from_path(pdf_path, 300)

    # Perform OCR on each image and combine the extracted text
    text = ""
    for page in pages:
        # Preprocess the image
        preprocessed_image = preprocess_image(page)

        # Perform OCR on the preprocessed image
        text += pytesseract.image_to_string(preprocessed_image)

    return text

# Helper function to extract relevant information using GPT (ChatGPT or other AI model)
def extract_information_with_gpt(text):
    """
    This function uses OpenAI's GPT model to analyze the OCR text and extract key information
    in a properly formatted JSON structure.
    """
    prompt = f"""
    Analyze the following text and extract the relevant business information. 
    Return ONLY a JSON object with the following structure, and ensure all values are strings:
    {{
        "company_name": "name or null if not found",
        "company_identifier": "identifier or null if not found",
        "document_purpose": "purpose or null if not found",
        "additional_information": {{
            "key_points": ["point1", "point2", etc.]
        }}
    }}

    If any information is not found, use null instead of leaving it empty or writing "not mentioned".
    Ensure the response is a valid JSON object that can be parsed by json.loads().
    Only returned the information requested, do not provide interactive messages like "Certainly, here is the..."
    Translate the values for the following keys: document_purpose, additional_information and key_points from whichever language they are in into English
    When the additional information contains a temporal expression (e.g. from "today", as of "today") but we don't know when that "today" happened,
    add between parenthesis the date of the document, if there is one. 

    Text to analyze:
    {text}
    """

    # Update to use the new OpenAI chat completions API
    response = client.chat.completions.create(
        model="gpt-4", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,  # Limit the response length
        temperature=0.5  # Middle ground between focused responses and imaginative responses. 
    )
    
    # Parse and return the response from GPT
    extracted_data = response.choices[0].message.content.strip()

    try:
        # Try to parse the extracted data as JSON
        return json.loads(extracted_data)
    except json.JSONDecodeError:
        # If it fails to parse, return the raw text instead
        return {"error": "Unable to parse extracted data", "data": extracted_data}

# Main function to process multiple PDF files in a directory and extract information
def process_belgian_gazette_pdfs(pdf_dir):
    """
    This function processes all PDFs in the provided directory, converts them to images,
    and extracts text using OCR. It then uses OpenAI GPT to extract the information we are looking for.
    """
    extracted_data = []

    # Loop through each PDF file in the directory
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            # Construct the relative path to the PDF file
            pdf_path = os.path.join(pdf_dir, filename)
            
            print(f"Processing {filename}...")

            # Extract text from the PDF using OCR
            text = extract_text_from_pdf(pdf_path)
            
            # Extract relevant information from the OCR text using GPT
            extracted_info = extract_information_with_gpt(text)
            
            # Append the extracted information to the results list
            extracted_data.append(extracted_info)

    return extracted_data

# Function to save extracted information to a JSON file
def save_to_json(data, output_file):
    """
    This function saves the extracted data to a JSON file.
    """
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Example usage
if __name__ == "__main__":

    # Process the PDFs and extract data
    extracted_info = process_belgian_gazette_pdfs(pdf_directory)
    
    # Save the extracted information to a JSON file
    save_to_json(extracted_info, "extracted_info.json")
    print("Extracted information saved to 'extracted_info.json'")