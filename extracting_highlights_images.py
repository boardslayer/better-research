import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import os
import json

def load_config(config_file="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_file}, using defaults")
        return {
            "extraction": {
                "extract_highlights": True,
                "extract_handwriting": True
            }
        }
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}, using defaults")
        return {
            "extraction": {
                "extract_highlights": True,
                "extract_handwriting": True
            }
        }

def extract_highlights_and_red_annotations(pdf_path, output_dir="extracted_content", config=None):
    """
    Extract yellow highlights and red marker annotations as images from a PDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted images
        config (dict): Configuration dictionary with extraction options
    """
    
    # Load config if not provided
    if config is None:
        config = load_config()
    
    # Get extraction settings
    extract_highlights = config.get("extraction", {}).get("extract_highlights", True)
    extract_handwriting = config.get("extraction", {}).get("extract_handwriting", True)
    
    print(f"🔍 Extraction settings:")
    print(f"   - Yellow highlights: {'✅ Enabled' if extract_highlights else '❌ Disabled'}")
    print(f"   - Red handwriting: {'✅ Enabled' if extract_handwriting else '❌ Disabled'}")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    extracted_items = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get page as image with high resolution
        mat = fitz.Matrix(3.0, 3.0)  # 3x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Convert to numpy array for OpenCV processing
        nparr = np.frombuffer(img_data, np.uint8)
        page_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if page_img is None:
            print(f"Warning: Could not convert page {page_num + 1} to image")
            continue
        
        # Extract annotations (highlights, ink annotations, etc.)
        annotations = page.annots()
        
        for annot in annotations:
            annot_type = annot.type[1]  # Get annotation type name
            
            # Check for yellow highlights or red ink annotations
            if should_extract_annotation(annot, annot_type, extract_highlights, extract_handwriting):
                rect = annot.rect
                
                # Convert PDF coordinates to image coordinates (accounting for zoom)
                x1 = int(rect.x0 * 3.0)
                y1 = int(rect.y0 * 3.0)
                x2 = int(rect.x1 * 3.0)
                y2 = int(rect.y1 * 3.0)
                
                # Add padding around the annotation
                padding = 10
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(page_img.shape[1], x2 + padding)
                y2 = min(page_img.shape[0], y2 + padding)
                
                # Extract the region
                extracted_region = page_img[y1:y2, x1:x2]
                
                if extracted_region.size > 0:
                    # Save the extracted region
                    filename = f"page_{page_num + 1}_{annot_type}_{len(extracted_items) + 1}.png"
                    filepath = os.path.join(output_dir, filename)
                    cv2.imwrite(filepath, extracted_region)
                    
                    extracted_items.append({
                        "page": page_num + 1,
                        "type": annot_type,
                        "filename": filename,
                        "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                    })
                    
                    print(f"Extracted {annot_type} from page {page_num + 1}: {filename}")
        
        # Also try to detect highlights and red marks using detection
        color_based_extractions = extract_by_color_detection(page_img, page_num, output_dir, len(extracted_items), extract_highlights, extract_handwriting)
        extracted_items.extend(color_based_extractions)
    
    doc.close()
    
    # Save extraction summary
    summary_file = os.path.join(output_dir, "extraction_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(extracted_items, f, indent=2)
    
    print(f"\nExtraction complete! Found {len(extracted_items)} items.")
    print(f"Images saved to: {output_dir}")
    print(f"Summary saved to: {summary_file}")
    
    return extracted_items

def should_extract_annotation(annot, annot_type, extract_highlights=True, extract_handwriting=True):
    """
    Determine if an annotation should be extracted based on type, color, and configuration.
    
    Args:
        annot: The annotation object
        annot_type: Type of annotation
        extract_highlights: Whether to extract yellow highlights
        extract_handwriting: Whether to extract red handwriting/annotations
    """
    # Check for highlight annotations
    if annot_type in ["Highlight", "Squiggly", "StrikeOut", "Underline"]:
        if not extract_highlights:
            return False
        # Check if it's yellow-ish
        color = annot.colors.get("stroke", annot.colors.get("fill", [0, 0, 0]))
        if color and len(color) >= 3:
            r, g, b = color[:3]
            # Yellow highlights typically have high red and green, low blue
            if r > 0.7 and g > 0.7 and b < 0.5:
                return True
    
    # Check for ink annotations (marker/pen annotations)
    elif annot_type in ["Ink", "FreeText"]:
        if not extract_handwriting:
            return False
        color = annot.colors.get("stroke", [0, 0, 0])
        if color and len(color) >= 3:
            r, g, b = color[:3]
            # Red markers typically have high red, low green and blue
            if r > 0.7 and g < 0.3 and b < 0.3:
                return True
    
    return False

def merge_nearby_rectangles(rectangles, horizontal_threshold=50, vertical_threshold=30):
    """
    Merge rectangles that are close to each other to form logical groups.
    
    Args:
        rectangles: List of (x, y, w, h) tuples
        horizontal_threshold: Maximum horizontal distance to merge
        vertical_threshold: Maximum vertical distance to merge
    
    Returns:
        List of merged rectangles
    """
    if not rectangles:
        return []
    
    # Convert to (x1, y1, x2, y2) format for easier processing
    rects = [(x, y, x + w, y + h) for x, y, w, h in rectangles]
    
    merged = []
    used = [False] * len(rects)
    
    for i, rect1 in enumerate(rects):
        if used[i]:
            continue
            
        # Start a new group with this rectangle
        group = [rect1]
        used[i] = True
        
        # Keep trying to add more rectangles to this group
        changed = True
        while changed:
            changed = False
            for j, rect2 in enumerate(rects):
                if used[j]:
                    continue
                
                # Check if rect2 should be merged with any rectangle in the current group
                should_merge = False
                for group_rect in group:
                    if rectangles_should_merge(group_rect, rect2, horizontal_threshold, vertical_threshold):
                        should_merge = True
                        break
                
                if should_merge:
                    group.append(rect2)
                    used[j] = True
                    changed = True
        
        # Calculate bounding box for the entire group
        min_x = min(rect[0] for rect in group)
        min_y = min(rect[1] for rect in group)
        max_x = max(rect[2] for rect in group)
        max_y = max(rect[3] for rect in group)
        
        merged.append((min_x, min_y, max_x - min_x, max_y - min_y))
    
    return merged

def rectangles_should_merge(rect1, rect2, horizontal_threshold, vertical_threshold):
    """
    Determine if two rectangles should be merged based on proximity.
    """
    x1_1, y1_1, x2_1, y2_1 = rect1
    x1_2, y1_2, x2_2, y2_2 = rect2
    
    # Check for overlap or close proximity
    
    # Horizontal overlap or close horizontal distance
    h_overlap = not (x2_1 < x1_2 - horizontal_threshold or x2_2 < x1_1 - horizontal_threshold)
    
    # Vertical overlap or close vertical distance  
    v_overlap = not (y2_1 < y1_2 - vertical_threshold or y2_2 < y1_1 - vertical_threshold)
    
    return h_overlap and v_overlap

def extract_by_color_detection(page_img, page_num, output_dir, start_index, extract_highlights=True, extract_handwriting=True):
    """
    Extract content using color detection for yellow highlights and red marks.
    Merges nearby regions into logical groups.
    
    Args:
        page_img: Page image
        page_num: Page number
        output_dir: Output directory
        start_index: Starting index for naming
        extract_highlights: Whether to extract yellow highlights
        extract_handwriting: Whether to extract red handwriting
    """
    extracted_items = []
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(page_img, cv2.COLOR_BGR2HSV)
    
    # Process yellow highlights if enabled
    if extract_highlights:
        # Define ranges for yellow highlights
        yellow_lower = np.array([15, 50, 50])
        yellow_upper = np.array([35, 255, 255])
        
        # Process yellow highlights
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Get individual rectangles for yellow highlights
        yellow_rects = []
        for contour in yellow_contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                yellow_rects.append((x, y, w, h))
        
        # Merge nearby yellow rectangles
        merged_yellow = merge_nearby_rectangles(yellow_rects, horizontal_threshold=100, vertical_threshold=50)
        
        # Extract merged yellow regions
        for i, (x, y, w, h) in enumerate(merged_yellow):
            # Add padding
            padding = 15
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(page_img.shape[1], x + w + padding)
            y2 = min(page_img.shape[0], y + h + padding)
            
            extracted_region = page_img[y1:y2, x1:x2]
            
            if extracted_region.size > 0:
                filename = f"page_{page_num + 1}_yellow_highlight_group_{start_index + len(extracted_items) + 1}.png"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, extracted_region)
                
                extracted_items.append({
                    "page": page_num + 1,
                    "type": "yellow_highlight_group",
                    "filename": filename,
                    "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "individual_regions": len([r for r in yellow_rects if rectangles_overlap((x, y, w, h), r)])
                })
                
                print(f"Extracted yellow highlight group on page {page_num + 1}: {filename}")
    
    # Process red marks if enabled
    if extract_handwriting:
        # Define ranges for red marks
        red_lower1 = np.array([0, 50, 50])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 50, 50])
        red_upper2 = np.array([180, 255, 255])
        
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = red_mask1 + red_mask2
        
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Get individual rectangles for red marks
        red_rects = []
        for contour in red_contours:
            area = cv2.contourArea(contour)
            if area > 200:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                red_rects.append((x, y, w, h))
        
        # Merge nearby red rectangles (more aggressive merging for connected text/marks)
        merged_red = merge_nearby_rectangles(red_rects, horizontal_threshold=80, vertical_threshold=40)
        
        # Extract merged red regions
        for i, (x, y, w, h) in enumerate(merged_red):
            # Add padding
            padding = 15
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(page_img.shape[1], x + w + padding)
            y2 = min(page_img.shape[0], y + h + padding)
            
            extracted_region = page_img[y1:y2, x1:x2]
            
            if extracted_region.size > 0:
                filename = f"page_{page_num + 1}_red_mark_group_{start_index + len(extracted_items) + 1}.png"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, extracted_region)
                
                extracted_items.append({
                    "page": page_num + 1,
                    "type": "red_mark_group",
                    "filename": filename,
                    "coordinates": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "individual_regions": len([r for r in red_rects if rectangles_overlap((x, y, w, h), r)])
                })
                
                print(f"Extracted red mark group on page {page_num + 1}: {filename}")
    
    return extracted_items

def rectangles_overlap(rect1, rect2):
    """Check if two rectangles overlap."""
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def main():
    """Main function to run the extraction."""
    import os
    import sys
    # Ensure the script is run with a valid PDF path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:        # Default PDF path if not provided
        pdf_path = "Coldwell22.pdf"
  
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found!")
        return
    
    # Create new output directory for grouped extractions
    output_dir = "extracted_content_grouped"
    
    print(f"Starting extraction from: {pdf_path}")
    print("Looking for yellow highlights and red marker annotations...")
    print("Using improved grouping algorithm to merge nearby regions...")
    
    # Load configuration
    config = load_config()
    
    extracted_items = extract_highlights_and_red_annotations(pdf_path, output_dir, config)
    
    if extracted_items:
        print(f"\n✅ Successfully extracted {len(extracted_items)} grouped items!")
        
        # Count by type
        yellow_groups = [item for item in extracted_items if 'yellow' in item['type']]
        red_groups = [item for item in extracted_items if 'red' in item['type']]
        
        print("\n 📊  Summary:")
        print(f"  - {len(yellow_groups)} yellow highlight groups")
        print(f"  - {len(red_groups)} red mark groups")
        
        # Show total individual regions that were merged
        total_individual_yellow = sum(item.get('individual_regions', 1) for item in yellow_groups)
        total_individual_red = sum(item.get('individual_regions', 1) for item in red_groups)
        
        print("\n🔗 Merging efficiency:")
        print(f"  - Yellow: {total_individual_yellow} individual regions → {len(yellow_groups)} groups")
        print(f"  - Red: {total_individual_red} individual regions → {len(red_groups)} groups")
        
        print(f"\n📁 Output saved to: {output_dir}/")
        
        print("\nExtracted groups:")
        for item in extracted_items:
            regions_info = f" (merged {item.get('individual_regions', 1)} regions)" if item.get('individual_regions', 1) > 1 else ""
            print(f"  - Page {item['page']}: {item['type']}{regions_info} -> {item['filename']}")
    else:
        print("\n⚠️  No highlighted content or red annotations found.")
        print("This could mean:")
        print("  - The PDF doesn't contain the specified annotations")
        print("  - The annotations are in a different format")
        print("  - The detection thresholds need adjustment")

if __name__ == "__main__":
    main()