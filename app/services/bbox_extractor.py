import pytesseract
from pytesseract import Output


def extract_bounding_boxes(image):

    # Use default OCR config but with slightly lower confidence threshold
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    boxes = []

    for i in range(len(data['text'])):
        text = data['text'][i].strip()

        # Lower confidence threshold to capture more text
        if text != "" and int(data['conf'][i]) > 30:
            boxes.append({
                "text": text,
                "x": data['left'][i],
                "y": data['top'][i],
                "w": data['width'][i],
                "h": data['height'][i]
            })

    return boxes
