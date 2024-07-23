from dotenv import load_dotenv
load_dotenv()  # Load all the environment variables from .env

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Configure the generative AI with the API key
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API key not found. Please check your .env file.")

# Load the new model
model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(input, image, user_prompt):
    try:
        response = model.generate_content([input, image[0], user_prompt])
        return response.text
    except Exception as e:
        st.error(f"Error in generating response: {e}")
        return None

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize our Streamlit app
st.set_page_config(page_title="MultiLanguage Invoice Extractor")

st.header("MultiLanguage Invoice Extractor")
input_prompt = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image of the invoice...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Tell me about the invoice")

# Define the initial prompt for the AI
initial_prompt = """
You are an expert in understanding invoices. We will upload an image of an invoice,
and you will have to answer any questions based on the uploaded invoice image.
"""

# If submit button is clicked
if submit:
    if uploaded_file is not None:
        image_data = input_image_details(uploaded_file)
        response = get_gemini_response(initial_prompt, image_data, input_prompt)
        if response:
            st.subheader("The Response is:")
            st.write(response)
    else:
        st.error("Please upload an image file.")
