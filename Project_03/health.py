from dotenv import load_dotenv
import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Load all environment variables
load_dotenv()

# Configure the API key for Google Gemini 1.5 Flash
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key not found. Please ensure it is set in the .env file.")
else:
    genai.configure(api_key=api_key)

# Function to load Google Gemini 1.5 Flash API and get response
def get_gemini_response(input_text, image_data, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_text, image_data[0], prompt])

        if response and response.candidates:
            text_response = response.candidates[0].content.parts[0].text
            
            # Check if the AI mentions it cannot calculate calories and handle it
            if "I am an AI and I cannot perform actions" in text_response:
                return "The AI could not calculate the calories accurately. Please provide a different image or prompt."
            else:
                return text_response
        else:
            return "Error: No valid response received from API."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to set up image input for API
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        # Open the image using PIL
        image = Image.open(uploaded_file)

        # Optionally resize or process the image before sending
        image = image.convert("RGB")
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": img_byte_arr
            }
        ]
        return image_parts
    else:
        st.error("Please upload an image file.")
        return None

# Initialize Streamlit app
st.set_page_config(page_title="Gemini Health App")
st.header("Gemini Health App")

# Input fields
input_text = st.text_input("Input Prompt:", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# Set up the prompt for calorie calculation
input_prompt = """
You are an expert nutritionist AI. Based on your training data, estimate the calorie content of the food items in the image. 
Even if you don't have all the details, provide an estimated calorie count for each food item visible, assuming typical preparation methods and ingredients.

Please provide the information in the following format:
1. Item 1 - estimated number of calories
2. Item 2 - estimated number of calories
...
"""


# On submit, process the image and generate a response
if st.button("Tell me the total calories"):
    image_data = input_image_setup(uploaded_file)
    if image_data:
        response = get_gemini_response(input_text, image_data, input_prompt)
        st.subheader("The Response is:")
        st.write(response)
    else:
        st.error("Image processing failed. Please try again.")
