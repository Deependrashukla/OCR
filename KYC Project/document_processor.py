from common_library import *
import pan_card
import aadhar_card
import driving_license


class DocumentProcessor:
    def __init__(self, image_path, processor_id):
        self.processor_id = processor_id
        self.image_path = image_path

    def correct_image_orientation(self, img):
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
            # cases: image doesn't have getexif
            pass
        return img

    def process_document(self):
        if self.image_path is not None:
            # Open the image file
            img = Image.open(self.image_path)
            img = self.correct_image_orientation(img)

            # Save the corrected image to a temporary file
            temp_image_path = "temp_image.jpg"
            img = img.convert("RGB")
            img.save(temp_image_path, quality=100)

            # Update the processor mapping to use the preprocessed image
            processor = self.get_processor(temp_image_path)
            details_json = processor.detect_and_process_regions()
        
        return details_json

    def get_processor(self, processed_image_path):
        # Use the preprocessed image path for further processing
        processor_mapping = {
            1: aadhar_card.AadhaarCardProcessor(processed_image_path),
            4: driving_license.LicenceCardProcessor(processed_image_path),
            5: pan_card.PanCardProcessor(processed_image_path)
        }

        if self.processor_id not in processor_mapping:
            raise ValueError(f"Processor with ID {self.processor_id} is not recognized.")

        return processor_mapping[self.processor_id]


# # Usage example
# uploaded_image_path = "abhipsa biswas.jpeg"
# processor_id = 1  # This would depend on the type of document (Aadhaar, PAN, etc.)

# # Instantiate the processor with the uploaded image path and processor ID
# processor = DocumentProcessor(uploaded_image_path, processor_id)

# # Process the document to correct orientation and extract details
# extracted_details = processor.process_document()
# print(extracted_details)



