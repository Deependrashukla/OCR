from ocr import OCR

ocr=OCR(image_folder=r"C:\Users\Deepender Shukla\Downloads\test")


if __name__ == "__main__":
    ocr.keras_ocr_works()
    ocr.easyocr_model_works()
    ocr.pytesseract_model_works()