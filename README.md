# Summary
This script is designed to process scanned PDFs (not text-based). It transforms the PDFs into images, preprocesses the images to make them easier for the OCR to read, performs OCR on the images which extracts text, then uses OpenAI's API to find relevant information and translates it to English. Finally, it saves the results in a separate file in JSON format. 

# Necessary installations
If you don't already have Python installed, download it (make sure to add it to PATH). You need at least Python 3.6 and Python 3.12 at most, as Tesseract so far only supports up to this last version. 

For Tesseract, you can download it from this link: https://github.com/UB-Mannheim/tesseract/wiki

You also need to install an IDE of your choice, I used VS Code.

To use OpenAI's API, you need to pay for a secret key, but for this task it was not expensive. I put $5 and used less than $3. 

You need to install the following using pip from cmd:
- pytesseract - this is the OCR
- openai - to be able to interact with OpenAI's API
- pdf2image - to convert the PDFs into images
- dotenv - to store the key securely in a separate file and not compromise its secrecy, and to add a path to the pdfs directory
- opencv-pyhton - to preprocess the images to make them easier for the OCR to read
- pillow - so pdf2image can work correctly
- numpy - necessary for OpenCV to run correctly
- poppler - for handling the pdfs' pages, necessary for pdf2image

Add pytesseract and poppler to PATH. 

# More detail on using the secret key
Create an .env file in your project directory, you can do it from your IDE. Ensure that you use the same naming convention that I used, in this case OPEN_API_KEY, then add an equal (no spaces) and paste your key. When you first obtain the key, you will only have one chance of seeing it complete, after that it will be partially hidden in the OpenAI website, so copy it when you first see it. It should begin with an sk. What you should have in your .env looks like this OPEN_API_KEY=sk...etc.

# More detail on pdf_directory
As you may store the PDF files in a different place to me, please add the path to wherever you store them there. For example PDF_DIRECTORY=C:/Users/YourName/Documents/Task 1 folder/PDFs - Change the \ splashes into either double \\ or forward /, due to particularities of Python's syntax.

