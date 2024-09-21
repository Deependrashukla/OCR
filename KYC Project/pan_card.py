from common_library import *

class PanCardProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def extract_text_from_image_pytesseract(self, image):
        text = pytesseract.image_to_string(image)
        return text.strip()

    def extract_details(self, extracted_text):
        dob_pattern = re.compile(r'\b(\d{2}[\/0-9]\d{2}[\/0-9]\d{4})\b')
        dob_match = dob_pattern.search(extracted_text)
        dob = dob_match.group(1) if dob_match else None

        pan_pattern = re.compile(r'\b([A-Za-z]{5}\d{4}[A-Za-z])\b')
        pan_match = pan_pattern.search(extracted_text)
        pan_number = pan_match.group(1) if pan_match else None

        try:
            dob_index = extracted_text.index(f"{dob}")
            names_text = extracted_text[: dob_index]
            lines = names_text.split('\n')[:-2]
        except:
            names_text = extracted_text
            lines = names_text.split('\n')[:-1]

        if dob:
            dob = re.sub(r'(\d{2})[\/0-9](\d{2})[\/0-9](\d{4})', r'\1/\2/\3', dob)

        capital_word_pattern = re.compile(r'\b[A-Z]+\b')
        capital_words_grouped = []

        for line in lines:
            capital_words = ' '.join(capital_word_pattern.findall(line))
            if capital_words and len(capital_words.replace(' ', '')) > 3 and ' ATH' not in capital_words:
                capital_words_grouped.append(capital_words)

        try:
            Name = capital_words_grouped[-2]
        except:
            Name = None

        try:
            Father_Name = capital_words_grouped[-1]
        except:
            Father_Name = None

        details = {
            "Name": Name,
            "Father's Name": Father_Name,
            "DOB": dob,
            "Id Number": pan_number,
            "Address":None
        }

        details_json = json.dumps(details, indent=4)
        return details_json

    def detect_and_process_regions(self):
        faces = self.face_cascade.detectMultiScale(self.gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        height, width = self.image.shape[:2]
        all_text_pytesseract = ""

        for (x, y, w, h) in faces:
            x1 = max(0, x - w)
            y1 = min(height, y)
            x2 = min(width, x1 + int(w * 7.5))
            y2 = min(height, y1 + (h * 6))

            cv2.rectangle(self.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(self.image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cropped_image = self.gray_image[y1:y2, x1:x2]
            text_pytesseract = self.extract_text_from_image_pytesseract(cropped_image)
            all_text_pytesseract += text_pytesseract + "\n"

            x3 = max(0, x - w * 6)
            y3 = max(0, y - h * 2)
            x4 = min(width, x3 + int(w * 5))
            y4 = min(height, y + h * 2)

            if x > x4:
                cv2.rectangle(self.image, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cropped_image = self.gray_image[y3:y4, x3:x4]
                text_pytesseract = self.extract_text_from_image_pytesseract(cropped_image)
                all_text_pytesseract += text_pytesseract + "\n"

        details_pytesseract = self.extract_details(all_text_pytesseract)
        return details_pytesseract

# # Example usage
# image_path = 'medini.jpeg'
# processor = PanCardProcessor(image_path)
# details = processor.detect_and_process_regions()
# print(details)



