from common_library import *

class LicenceCardProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def extract_text_from_image_pytesseract(self, image):
        text = pytesseract.image_to_string(image)
        return text.strip()

    def extract_details(self, extracted_text):
        licence_pattern = re.compile(r'(.{5}\d{11})\b')
        licence_match = licence_pattern.search(extracted_text)
        licence_number = licence_match.group(0) if licence_match else None

        address_pattern = re.compile(
            r'(?:Address\s*: \s*(.*?\d{5,6}\s))|(?::(?!.*:.*\d{5,6}\s)(.{0,200}[\n\s]\d{5,6}\s))',
            re.DOTALL | re.MULTILINE)
        address_match = address_pattern.search(extracted_text)
        
        if address_match:
            end_name_dob = extracted_text.find(address_match.group(1) or address_match.group(2))
            address = (address_match.group(1) or address_match.group(2)).strip().replace('\n', ' ')
            if len(address) < 15:
                address_pattern = re.compile(r'((?:.*\n){2}.*\d{5,6}\s*)', re.MULTILINE)
                address_match = address_pattern.search(extracted_text)
                end_name_dob = extracted_text.find(address_match.group(1) or address_match.group(2))
                address = address_match.group(1).strip().replace('\n', ' ')
        elif pattern := re.compile(r'((?:.*\n){2}.*\d{5,6}\s*)', re.MULTILINE).search(extracted_text):
            end_name_dob = extracted_text.find(address_match.group(1) or address_match.group(2))
            address = pattern.group(1).strip().replace('\n', ' ')
        else:
            end_name_dob = len(extracted_text)
            address = None

        if address:
            noise_chars = ('|', '+', '=', ';', '@', '$', '&', '\\', '*', '>', '<')
            noise_pattern = '[' + re.escape(''.join(noise_chars)) + ']'
            address = re.sub(noise_pattern, '', address)
            address = re.sub(r'\s+', ' ', address).strip()

        if licence_number:
            start_name_dob = extracted_text.find('\n', extracted_text.find(licence_number))
        else:
            start_name_dob = 0

        if start_name_dob < end_name_dob:
            text_name_dob = extracted_text[start_name_dob:end_name_dob]
        else:
            text_name_dob = extracted_text[:end_name_dob]

        capital_word_pattern = re.compile(r'\b[A-Z]+\b')
        capital_words_grouped = []
        lines = text_name_dob.split('\n')
        Name = None

        for line in lines:
            capital_words = ' '.join(capital_word_pattern.findall(line))
            Name = capital_words if capital_words and len(capital_words.replace(' ','')) > 3 and 'Name' in capital_words else None
            if capital_words and len(capital_words.replace(' ','')) > 3:
                capital_words_grouped.append(capital_words)

        try:
            if Name is None:
                Name = capital_words_grouped[0]
        except:
            Name = None

        if Name:
            text_name_dob = text_name_dob[text_name_dob.find(Name):]

        dob_pattern1 = re.compile(r'\b(?:DOB|Date\s+of\s+Birth)\s*[:\-]?\s*(\d{2}[\/\-0-9]\d{2}[\/\-0-9]\d{4})', re.IGNORECASE)
        dob_pattern2 = re.compile(r'((\d{2}[\/-]\d{2}[\/-]\d{4}))')

        if dob_match := dob_pattern1.search(extracted_text):
            dob = dob_match.group(1)
        elif dob_match := dob_pattern2.search(text_name_dob):
            dob = dob_match.group(1)
        else:
            dob = None

        if dob:
            dob = re.sub(r'(\d{2})[\/0-9](\d{2})[\/0-9](\d{4})', r'\1/\2/\3', dob)

        details = {
            "Name": Name,
            "DOB": dob,
            "Id Number": licence_number, 
            "Address": address
        }

        details_json = json.dumps(details, indent=4, ensure_ascii=False)
        return details_json

    def detect_and_process_regions(self):
        faces = self.face_cascade.detectMultiScale(self.gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        height, width = self.image.shape[:2]
        all_text_pytesseract = ""

        for (x, y, w, h) in faces:
            x1 = max(0, x - w * 8)
            y1 = max(0, y - int(h * 1.5))
            x2 = min(width, x)
            y2 = min(height, y + (h * 4))

            cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cropped_image = self.gray_image[y1:y2, x1:x2]
            text_pytesseract = self.extract_text_from_image_pytesseract(cropped_image)
            all_text_pytesseract += text_pytesseract + "\n"

        details_pytesseract = self.extract_details(all_text_pytesseract)
        return details_pytesseract

# Example usage
# image_path = 'pinky.jpeg'
# processor = LicenceCardProcessor(image_path)
# details = processor.detect_and_process_regions()
# print(details)


