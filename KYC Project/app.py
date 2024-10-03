import document_processor
from flask import Flask, request, jsonify, Response
import shutil
import os
import requests
import json

app = Flask(__name__)

def download_file(url, local_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)
        else:
            raise Exception(f"Failed to download file: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error downloading file: {e}")

@app.route('/process_documents', methods=['POST'])
def process_documents():
    try:
        # Get data from request
        data = request.get_json()
        auth_header = request.headers.get('Authorization')
        
        front_image_path = data.get('front_image_path')
        back_image_path = data.get('back_image_path')
        doc_insert_id = data.get('doc_insert_id')
        nat_id = data.get('nat_id')

        
        if not front_image_path and not back_image_path:
            return jsonify({"error": "Invalid input, please provide any one or both images front_image_path, back_image_path, and doc_insert_id"}), 400
         
        if not doc_insert_id or not nat_id:
            return jsonify({"error": "Invalid input, please provide front_image_path, back_image_path, and doc_insert_id"}), 400
        
        # Create a folder to save images locally
        folder_path = str(doc_insert_id)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        front_details = {'Name': None, 'DOB': None, 'Id Number': None, 'Address': None}
        back_details = {'Name': None, 'DOB': None, 'Id Number': None, 'Address': None}
        
        if front_image_path:
            # Download the front image
            front_image_local_path = os.path.join(folder_path, 'front_image.jpg')
            download_file(front_image_path, front_image_local_path)

            # Process the front image
            front_processor = document_processor.DocumentProcessor(front_image_local_path, nat_id)
            front_details = front_processor.process_document()
        
        if back_image_path:
        # Download the back image
            back_image_local_path = os.path.join(folder_path, 'back_image.jpg')
            download_file(back_image_path, back_image_local_path)

            # Process the back image
            back_processor = document_processor.DocumentProcessor(back_image_local_path, nat_id)
            back_details = back_processor.process_document()

        # Combine the results
        combined_details = {
            "name": front_details.get('Name') or back_details.get('Name'),
            "dob": front_details.get('DOB') or back_details.get('DOB'),
            "id_number": front_details.get('Id Number') or back_details.get('Id Number'),
            "address": front_details.get('Address') or back_details.get('Address')
        }
        # Manually serialize the JSON
        response_json = json.dumps(combined_details)

        # Return the manual JSON response
        return Response(response_json, mimetype='application/json'), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
  

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)





