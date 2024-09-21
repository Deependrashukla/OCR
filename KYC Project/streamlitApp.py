from common_library import *
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pan_card
import aadhar_card
import driving_license
import streamlit as st

# from flask import Flask, jsonify
# from flask import request
# import requests
# import numpy as np 

# app = Flask(__name__) 

class DocumentProcessor:
    def __init__(self, image_path):
        # self.image_path = image_path
        # self.image = cv2.imread(image_path)
        # self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.processor_mapping = {
            'Pan Card': pan_card.PanCardProcessor(image_path),
            'Aadhar Card': aadhar_card.AadhaarCardProcessor(image_path),
            'Driving License': driving_license.LicenceCardProcessor(image_path)
        }
        # self.detected_faces = self.detect_faces()
        # self.detected_document_regions = self.detect_document_regions()
        # self.processed_documents = self.process_documents() 




    def get_details_with_least_nulls(self):
        extracted_details = {}

        for card_type, processor in self.processor_mapping.items():
            details_json = processor.detect_and_process_regions()
            details = json.loads(details_json)
            extracted_details[card_type] = details

        # Find the document with the least number of null values
        # In case of a tie, select the last one
        min_nulls_count = float('inf')
        min_nulls_document = None

        for card_type, details in extracted_details.items():
            null_count = sum(1 for v in details.values() if v in [None, 'null', ''])
            
            if null_count < min_nulls_count:
                min_nulls_count = null_count
                min_nulls_document = card_type
            elif null_count == min_nulls_count:
                # In case of a tie, select the last card_type with the same min_nulls_count
                min_nulls_document = card_type

        return json.dumps({min_nulls_document: extracted_details[min_nulls_document]}, indent=4)







# def download_image(image_url):
#     response = requests.get(image_url, stream=True)
#     if response.status_code == 200:
#         image = np.array(bytearray(response.content), dtype=np.uint8)
#         image = cv2.imdecode(image, cv2.IMREAD_COLOR)
#         temp_image_path = 'temp_image.jpg'
#         cv2.imwrite(temp_image_path, image)
#         return temp_image_path
#     else:
#         raise Exception("Image could not be retrieved.")

# @app.post('/process_document')
# def process_document():
#     try:
#         image_url = request.json['image_url']
#         image_path = download_image(image_url)
#         processor = DocumentProcessor(image_path)
#         result = processor.get_details_with_least_nulls()
#         return jsonify({"status": "success", "data": json.loads(result)}), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 400
    

# if __name__ == '__main__':
#     app.run(debug=True)


# Streamlit app
st.title("Aadhar/Pancard/Driving card details Extractor")


def correct_image_orientation(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(img._getexif().items())

        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    return img


# Upload an image file
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open the image file
    img = Image.open(uploaded_file)
    img = correct_image_orientation(img)
    # Save the image to a temporary file
    temp_image_path = "temp_image.jpg"
    img = img.convert("RGB")
    img.save(temp_image_path, quality = 100)

    # Process the image for document details
    processor = DocumentProcessor(temp_image_path)
    result = processor.get_details_with_least_nulls()
    # img = img.resize((500,400), Image.Resampling.LANCZOS)
    if st.button('Show Details'):
        st.write("Processed Document Details:")
        st.json(result)
        st.image(img, caption="Original Image", use_column_width=True)
        st.balloons()


# Example usage
# if __name__ == "__main__":
#     image_path = "abhipsa biswas.jpeg"
#     processor = DocumentProcessor(image_path)
#     result = processor.get_details_with_least_nulls()
#     print(result)


