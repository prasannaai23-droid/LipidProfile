from paddleocr import PaddleOCR
import cv2
import os
from collections import defaultdict
import csv

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    height, width = thresh.shape
    if width < 1000:
        scale = 1000 / width
        thresh = cv2.resize(thresh, (int(width*scale), int(height*scale)))

    processed_path = "processed_temp.png"
    cv2.imwrite(processed_path, thresh)
    return processed_path

def extract_text_from_image(image_path):
    processed_image = preprocess_image(image_path)
    ocr = PaddleOCR(use_textline_orientation=True)
    result = ocr.predict(processed_image)

    if not result:
        print("⚠️ OCR detected no text in this image. Try higher quality or clearer text.")
        return []

    rows = defaultdict(list)
    for line in result:
        for word_info in line:
            bbox = word_info[0]
            # Safe text extraction
            if isinstance(word_info[1], tuple):
                text = word_info[1][0]
            else:
                text = word_info[1]

            y_coord = int(sum([p[1] for p in bbox]) / 4)
            x_coord = int(sum([p[0] for p in bbox]) / 4)
            rows[y_coord].append((x_coord, text))

    sorted_rows = sorted(rows.items())
    table = []
    for _, words in sorted_rows:
        words_sorted = sorted(words, key=lambda x: x[0])
        line_text = [w[1] for w in words_sorted]
        table.append(line_text)

    if os.path.exists(processed_image):
        os.remove(processed_image)

    return table

def save_table_to_csv(table, csv_path):
    if not table:
        print("⚠️ No data to save to CSV.")
        return
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(table)

if __name__ == "__main__":
    image_path = r"C:\Users\HP\OneDrive\Desktop\pvy\ml-model-project\ml_model\report.png"
    csv_output_path = r"C:\Users\HP\OneDrive\Desktop\pvy\ml-model-project\ml_model\report_extracted.csv"

    table = extract_text_from_image(image_path)
    save_table_to_csv(table, csv_output_path)

    if table:
        print(f"\n✅ Text extracted and saved to CSV: {csv_output_path}")
    else:
        print("\n⚠️ No text extracted. Please try a clearer or higher resolution image.")
