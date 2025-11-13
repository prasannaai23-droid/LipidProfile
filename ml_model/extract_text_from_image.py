import cv2
import numpy as np
from paddleocr import PaddleOCR
import re
import os
import sys

# Initialize PaddleOCR (English) - Fixed parameters
ocr = PaddleOCR(use_textline_orientation=True, lang='en', device='cpu')

# -----------------------------
# 1️⃣ OCR text extraction
# -----------------------------
def extract_text_from_image(image_path):
    """Extract text using PaddleOCR"""
    try:
        # Read original image (PaddleOCR handles preprocessing internally)
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image at {image_path}")
        
        # Use the predict() method
        result = ocr.predict(img)
        
        if not result:
            return ""

        lines = []
        
        # Handle OCRResult objects from PaddleOCR 3.x
        for batch in result:
            if not batch:
                continue
            
            # OCRResult is a dict-like object with 'rec_texts' key
            if hasattr(batch, 'keys') and 'rec_texts' in batch:
                for text_item in batch['rec_texts']:
                    if text_item:  # Skip empty strings
                        lines.append(str(text_item))
        
        text = "\n".join(lines)
        return text
        
    except Exception as e:
        print(f"OCR Error: {e}")
        import traceback
        traceback.print_exc()
        return ""


# -----------------------------
# 2️⃣ Extract lipid values
# -----------------------------
def extract_lipid_values(image_path):
    """
    Extract lipid profile values from medical report image using OCR
    """
    try:
        # Get OCR text
        text = extract_text_from_image(image_path)
        
        if not text:
            return {"error": "Could not extract text from image"}
        
        print("\n" + "="*60)
        print("RAW OCR TEXT:")
        print("="*60)
        print(text)
        print("="*60 + "\n")
        
        # Initialize result dictionary
        result = {
            "raw_text": text,
            "patient_name": None,
            "age": None,
            "sex": None,
            "report_date": None,
            "total_cholesterol": None,
            "ldl": None,
            "hdl": None,
            "triglycerides": None,
            "vldl": None,
            "non_hdl": None,
            "tc_hdl_ratio": None,
            "tg_hdl_ratio": None,
            "ldl_hdl_ratio": None
        }
        
        # Extract patient info
        name_patterns = [
            r'Mr\.\s+([A-Za-z\s]+?)(?=\n|\d)',
            r'Mrs\.\s+([A-Za-z\s]+?)(?=\n|\d)',
            r'Ms\.\s+([A-Za-z\s]+?)(?=\n|\d)',
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                result["patient_name"] = name_match.group(1).strip()
                break
        
        # Extract age (fix: look for :27 YRS/M pattern)
        age_patterns = [
            r':(\d+)\s*YRS',
            r'Age[/\s:]+(\d+)\s*Y',
            r'(\d+)\s*YRS\s*/\s*[MF]',
        ]
        for pattern in age_patterns:
            age_match = re.search(pattern, text, re.IGNORECASE)
            if age_match:
                age_val = int(age_match.group(1))
                if 1 <= age_val <= 120:
                    result["age"] = age_val
                    break
        
        # Extract sex
        sex_patterns = [
            r':?\d+\s*YRS\s*/\s*([MF])',
            r'Sex[:\s]+([MF])',
        ]
        for pattern in sex_patterns:
            sex_match = re.search(pattern, text, re.IGNORECASE)
            if sex_match:
                result["sex"] = sex_match.group(1).upper()
                break
        
        # Extract date
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{1,2}-\d{1,2})',
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                result["report_date"] = date_match.group(1)
                break
        
        # Extract lipid values - looking for VALUE next to test name
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            line_upper = line.upper()
            
            # Skip empty or header lines
            if not line or line_upper in ['TEST', 'VALUE', 'UNIT', 'REFERENCE', 'BIOCHEMISTRY', 'LIPID PROFILE']:
                i += 1
                continue
            
            # Total Cholesterol - must come before any other cholesterol
            if line_upper == 'TOTAL CHOLESTEROL':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and not result["total_cholesterol"]:  # Only set if not already set
                        result["total_cholesterol"] = value
                        print(f"✓ Found Total Cholesterol: {value}")
            
            # Triglycerides
            elif line_upper == 'TRIGLYCERIDES':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and not result["triglycerides"]:
                        result["triglycerides"] = value
                        print(f"✓ Found Triglycerides: {value}")
            
            # HDL Cholesterol - exact match only
            elif line_upper == 'HDL CHOLESTEROL':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and not result["hdl"]:
                        result["hdl"] = value
                        print(f"✓ Found HDL: {value}")
            
            # LDL Cholesterol - exact match only
            elif line_upper == 'LDL CHOLESTEROL':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and not result["ldl"]:
                        result["ldl"] = value
                        print(f"✓ Found LDL: {value}")
            
            # VLDL Cholesterol - exact match only
            elif line_upper == 'VLDL CHOLESTEROL':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and not result["vldl"]:
                        result["vldl"] = value
                        print(f"✓ Found VLDL: {value}")
            
            # NON-HDL Cholesterol - exact match only
            elif line_upper == 'NON-HDL CHOLESTEROL':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and not result["non_hdl"]:
                        result["non_hdl"] = value
                        print(f"✓ Found Non-HDL: {value}")
            
            # LDL/HDL Ratio
            elif 'LDL' in line_upper and '/HDL' in line_upper and 'CHOLESTEROL' not in line_upper:
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and value < 10 and not result["ldl_hdl_ratio"]:
                        result["ldl_hdl_ratio"] = value
                        print(f"✓ Found LDL/HDL Ratio: {value}")
            
            # TC/HDL Ratio
            elif 'TOTAL CHOLESTEROL' in line_upper and '/ HDL' in line_upper:
                # Value might be 2 lines down (skipping 'L' marker)
                if i + 2 < len(lines):
                    value = extract_numeric_value(lines[i + 2])
                    if value and value < 10 and not result["tc_hdl_ratio"]:
                        result["tc_hdl_ratio"] = value
                        print(f"✓ Found TC/HDL Ratio: {value}")
            
            # TG/HDL Ratio
            elif line_upper == 'TG/HDL':
                if i + 1 < len(lines):
                    value = extract_numeric_value(lines[i + 1])
                    if value and value < 15 and not result["tg_hdl_ratio"]:
                        result["tg_hdl_ratio"] = value
                        print(f"✓ Found TG/HDL Ratio: {value}")
            
            i += 1
        
        # Validate extracted data
        required_fields = ["total_cholesterol", "ldl", "hdl", "triglycerides"]
        missing = [f for f in required_fields if not result.get(f)]
        
        if missing:
            print(f"\n⚠️ Warning: Missing required fields: {missing}")
        
        # Remove None values
        clean_result = {k: v for k, v in result.items() if v is not None and k != "raw_text"}
        
        if len(clean_result) < 4:  # Need at least patient info + some lipid values
            return {
                "error": "Could not extract sufficient data from image",
                "raw_text": text,
                "extracted": clean_result
            }
        
        print(f"\n✅ Successfully extracted {len(clean_result)} fields")
        return clean_result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"OCR extraction failed: {str(e)}"}


def extract_numeric_value(text):
    """Extract numeric value from text line"""
    cleaned = text.upper()
    cleaned = re.sub(r'MG/DL|MG\\DL|MGDL|MG\s*/\s*DL', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[A-Z]+\s*:', '', cleaned)
    cleaned = re.sub(r'[LH]$', '', cleaned)  # Remove L/H markers
    
    matches = re.findall(r'\b(\d+\.?\d*)\b', cleaned)
    
    if matches:
        for match in matches:
            try:
                num = float(match)
                if 0.1 <= num <= 500:
                    return num
            except ValueError:
                continue
    
    return None


if __name__ == "__main__":
    import sys
    
    default_path = os.path.join(os.path.dirname(__file__), "..", "uploads", "report.png")
    path = sys.argv[1] if len(sys.argv) > 1 else default_path

    print(f"\n🔍 Extracting from: {path}\n")

    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        sys.exit(1)

    try:
        values = extract_lipid_values(path)
        
        if "error" in values:
            print(f"\n❌ ERROR: {values['error']}")
            if "raw_text" in values:
                print("\nRaw Text Preview:")
                print(values["raw_text"][:500])
            if "extracted" in values:
                print("\nPartially extracted:")
                for k, v in values["extracted"].items():
                    print(f"  • {k}: {v}")
        else:
            print("\n✅ EXTRACTED VALUES:")
            for key, val in values.items():
                print(f"  • {key}: {val}")

    except Exception as e:
        import traceback
        print("\n❌ Error:", e)
        traceback.print_exc()
