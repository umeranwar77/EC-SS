import re
import os
import csv
import numpy as np
from paddleocr import PaddleOCR




def paddle_ocr(frame, x1, y1, x2, y2):
    """Extract text from license plate region"""
    cropped_frame = frame[y1:y2, x1:x2]
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang='en', ocr_version='PP-OCRv3')
    results = ocr.ocr(cropped_frame, det=False, rec=True, cls=False)
    
    for res in results:
        score = res[0][1]
        if not np.isnan(score) and score > 0.6:
            text = res[0][0]
            text = re.sub(r'[^\w]', '', text).replace("O", "0").replace("粤", "")
            return text,score
    return ""



def save_license_plates(license_plates, start_time, end_time):
    if not license_plates:
        print("No license plates detected in this interval.")
        return
    
    csv_file_path = "data_store/vehicle_license_plates.csv"
    file_exists = os.path.exists(csv_file_path)
    
    existing_entries = set()
    if file_exists:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  
            existing_entries = {(row[1], row[2]) for row in reader}
    
    with open(csv_file_path, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        
        if not file_exists:
            writer.writerow(["Timestamp", "Vehicle ID", "License Plate", "file_name","Confidence"])
        
        for plate_info in license_plates:
            if plate_info['plate']:
                if plate_info['vehicle_id'] not in existing_entries and plate_info['plate'] not in existing_entries:
                    writer.writerow([
                        end_time.isoformat(), 
                        plate_info['vehicle_id'], 
                        plate_info['plate'],
                        plate_info['crop_filename'], 
                        plate_info['confidence']
                    ])
                    existing_entries.add((plate_info['vehicle_id'], plate_info['plate']))