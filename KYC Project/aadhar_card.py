from common_library import *

class AadhaarCardProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.indian_states_and_uts = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
            "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Jammu and Kashmir", "Ladakh", "Delhi", "Puducherry", "Chandigarh", "Lakshadweep", 
            "Andaman and Nicobar Islands", "Dadra and Nagar Haveli and Daman and Diu" 
        ]



    def extract_text_from_image_pytesseract(self, image):
        text = pytesseract.image_to_string(image)
        return text.strip()
    
    def extract_text_with_details(self, image_path):
        try:
            image = cv2.imread(image_path)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_string(gray_image)
            return extracted_text
        except Exception as e:
            return "Error"
        
    def clean_and_extract_address(self, text):
        try:
            text = re.sub(r'\S+@\S+', '', text)
            text = re.sub(r'http\S+|www\S+', '', text)
            text = re.sub(r'\b\d{4} \d{3} \d{4}\b', '', text)
            match = re.search(r'\b(W/O|S/O|D/O|H/O)\b:\s*(.*)|address:\s*(.*)', text, re.DOTALL | re.IGNORECASE)
            if match:
                if match.group(1):  # If W/O|S/O|D/O|H/O was matched
                    address = (f'{match.group(1)}: {match.group(2)}')
                elif match.group(3):  # If address was matched
                    address = (match.group(3))

            
            address = re.sub(r'\b\w+\s*@®.*', '', address).strip()
            address = re.sub(r'[^\x00-\x7F]+', '', address)
            address = re.sub(r'[=]', '', address)
            address = re.sub(r'VID\s*:.*', '', address, flags=re.DOTALL)
            address = address.replace("|", "")

            pincode_match = re.search(r'(\d{6})\D*$', address)
            if pincode_match:
                pincode = pincode_match.group(1)
                address = address[:address.rfind(pincode) + 6]
            
            return address
        except Exception as e:
            return "Not Found"
                
    def extract_back_address(self, image_path):
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return self.clean_and_extract_address(text)
        except Exception as e:
            return "Not Found"


    def extract_address(self, image_path):
        high_conf_text = self.extract_text_with_details(image_path)
        if high_conf_text == "Error":
            return "Not Found"
        
        address = self.clean_and_extract_address(high_conf_text)
        if address == "Not Found":
            address = self.extract_back_address(image_path)
        return address

    def finalize_address(self, text):
        try:
            if "Not Found" in text:
                return None
            text = re.sub(r'^.*?\b(W/O|S/O|D/O|H/O)\b', lambda m: m.group(1), text, flags=re.IGNORECASE)
            text = re.sub(r'\bDate\b.*', '', text, flags=re.IGNORECASE)
            
            pincode_match = re.search(r'(\d{6})(?!.*\d{6})', text)
            if pincode_match:
                pincode = pincode_match.group(1)
                text = text[:text.rfind(pincode) + 6]
            
            pincodes = re.findall(r'\b\d{6}\b', text)
            if len(pincodes) > 1:
                last_pincode = pincodes[-1]
                text = re.sub(r'\b\d{6}\b', '', text).strip()
                text = text + ' ' + last_pincode
            
            for state in self.indian_states_and_uts:
                pattern = re.compile(r'\b' + re.escape(state) + r'\W*', re.IGNORECASE)
                text = pattern.sub(state, text)
            
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            return "Not Found"


    def extract_details(self, extracted_text):
        dob_pattern = re.compile(r'\b(\d{2}[\/0-9]\d{2}[\/0-9]\d{4})\b')
        dob_match = dob_pattern.search(extracted_text)
        dob = dob_match.group(1) if dob_match else None
        if dob:
            dob = re.sub(r'(\d{2})[\/0-9](\d{2})[\/0-9](\d{4})', r'\1/\2/\3', dob)

        aadhaar_pattern = re.compile(r'\b(\d{4} \d{4} \d{4})\b')
        aadhaar_match = aadhaar_pattern.search(extracted_text)
        aadhaar_number = aadhaar_match.group(1) if aadhaar_match else None

        name_near_dob_pattern = re.compile(r'\s*(.*)\n.*DOB|\s*(.*)\n\n.*DOB')
        name_match = name_near_dob_pattern.search(extracted_text)
        if name_match:
            name = name_match.group(1) or name_match.group(2)
            name = name.strip()
        else:
            name = None

        if dob_match:
            dob_start = dob_match.start()
            text_up_to_dob = extracted_text[:dob_start]
            lines = text_up_to_dob.split('\n')
            for i in range(len(lines) - 2, max(len(lines) - 4, -1), -1):
                line = lines[i].strip()
                if line:
                    name_near_dob = line
                    break
        else:
            name_near_dob = None

        name = (name or name_near_dob) if (name or name_near_dob) else None

        address_pattern = re.compile(r'Address:\s*(.*?)\n\n', re.DOTALL | re.IGNORECASE)
        address_match = address_pattern.search(extracted_text)
        address1 = address_match.group(1).strip() if address_match else None
        address2 = self.extract_address(self.image_path)
        final_address = self.finalize_address(address2)
        address = final_address if final_address else address1

        details = {
            "Name": name,
            "DOB": dob,
            "Id Number": aadhaar_number,
            "Address": address
        }

        details_json = json.dumps(details, indent=4)
        return details_json

    def detect_and_process_regions(self):
        faces = self.face_cascade.detectMultiScale(self.gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        height, width = self.image.shape[:2]
        all_text_pytesseract = ""

        for (x, y, w, h) in faces:
            x1 = max(0, x + w)
            y1 = max(0, y - h)
            x2 = min(self.image.shape[1], width - w)
            y2 = min(self.image.shape[0], y + h * 4)

            cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cropped_image = self.gray_image[y1:y2, x1:x2]
            text_pytesseract = self.extract_text_from_image_pytesseract(cropped_image)
            all_text_pytesseract += text_pytesseract + "\n"

        details_pytesseract = self.extract_details(all_text_pytesseract)
        return details_pytesseract



# # # Example usage
# image_path = 'address1.jpeg'
# processor = AadhaarCardProcessor(image_path)
# details = processor.detect_and_process_regions()
# print(details)



