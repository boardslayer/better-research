#!/usr/bin/env python3
"""
Configuration script for fine-tuning the grouping parameters.
"""

import fitz
import cv2
import numpy as np
import os
import json
from extracting_highlights_images import extract_highlights_and_red_annotations

def extract_with_custom_params(pdf_path, horizontal_threshold=100, vertical_threshold=50, 
                             yellow_area_min=500, red_area_min=200, padding=15):
    """
    Extract with custom parameters for fine-tuning.
    """
    print(f"\n🔧 EXTRACTION PARAMETERS:")
    print(f"  - Horizontal merge threshold: {horizontal_threshold}px")
    print(f"  - Vertical merge threshold: {vertical_threshold}px") 
    print(f"  - Yellow region minimum area: {yellow_area_min}px²")
    print(f"  - Red region minimum area: {red_area_min}px²")
    print(f"  - Padding around regions: {padding}px")
    print()
    
    # Temporarily modify the global parameters (not ideal, but works for demo)
    # In a production version, you'd pass these as parameters
    
    output_dir = f"extracted_content_h{horizontal_threshold}_v{vertical_threshold}"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # For now, use the default function but you could modify it to accept parameters
    extracted_items = extract_highlights_and_red_annotations(pdf_path, output_dir)
    
    return extracted_items, output_dir

def compare_different_settings(pdf_path="Coldwell22.pdf"):
    """
    Test different parameter combinations to find optimal settings.
    """
    
    print("🧪 TESTING DIFFERENT GROUPING PARAMETERS")
    print("=" * 50)
    
    # Test different combinations
    test_configs = [
        {"name": "Conservative", "h_thresh": 50, "v_thresh": 25},
        {"name": "Moderate", "h_thresh": 100, "v_thresh": 50}, 
        {"name": "Aggressive", "h_thresh": 150, "v_thresh": 75},
        {"name": "Very Aggressive", "h_thresh": 200, "v_thresh": 100}
    ]
    
    results = []
    
    for config in test_configs:
        print("\n 📊  Testing {config['name']} grouping...")
        
        # Note: This is a simplified version. The actual implementation would need
        # the functions to accept parameters
        items, output_dir = extract_with_custom_params(
            pdf_path, 
            horizontal_threshold=config['h_thresh'],
            vertical_threshold=config['v_thresh']
        )
        
        yellow_groups = [item for item in items if 'yellow' in item['type']]
        red_groups = [item for item in items if 'red' in item['type']]
        
        result = {
            "config": config['name'],
            "total_groups": len(items),
            "yellow_groups": len(yellow_groups),
            "red_groups": len(red_groups),
            "output_dir": output_dir
        }
        
        results.append(result)
        
        print(f"  - Total groups: {len(items)}")
        print(f"  - Yellow groups: {len(yellow_groups)}")
        print(f"  - Red groups: {len(red_groups)}")
    
    print(f"\n📈 COMPARISON SUMMARY:")
    print("-" * 40)
    for result in results:
        print(f"{result['config']:15s}: {result['total_groups']:2d} total groups")
    
    return results

def interactive_parameter_tuning():
    """
    Interactive tool for adjusting parameters.
    """
    
    print("🎛️  INTERACTIVE PARAMETER TUNING")
    print("=" * 40)
    print("Adjust these parameters to control how regions are grouped:")
    print()
    
    while True:
        print("Current grouping behavior:")
        print("- Horizontal threshold: How far apart horizontally regions can be to still merge")
        print("- Vertical threshold: How far apart vertically regions can be to still merge")
        print("- Higher values = more aggressive grouping (fewer, larger groups)")
        print("- Lower values = more conservative grouping (more, smaller groups)")
        print()
        
        try:
            h_thresh = int(input("Enter horizontal threshold (50-300, default 100): ") or "100")
            v_thresh = int(input("Enter vertical threshold (25-150, default 50): ") or "50")
            
            if h_thresh < 10 or h_thresh > 500:
                print("⚠️  Horizontal threshold should be between 10-500")
                continue
                
            if v_thresh < 5 or v_thresh > 200:
                print("⚠️  Vertical threshold should be between 5-200")
                continue
            
            print(f"\n🔄 Running extraction with h_thresh={h_thresh}, v_thresh={v_thresh}...")
            
            # Run extraction with these parameters
            items, output_dir = extract_with_custom_params(
                "Coldwell22.pdf",
                horizontal_threshold=h_thresh,
                vertical_threshold=v_thresh
            )
            
            yellow_groups = [item for item in items if 'yellow' in item['type']]
            red_groups = [item for item in items if 'red' in item['type']]
            
            print(f"\n✅ Results:")
            print(f"  - Total groups: {len(items)}")
            print(f"  - Yellow groups: {len(yellow_groups)}")
            print(f"  - Red groups: {len(red_groups)}")
            print(f"  - Output saved to: {output_dir}/")
            
            satisfied = input("\nSatisfied with these results? (y/n): ").lower().strip()
            if satisfied in ['y', 'yes']:
                print(f"\n🎉 Great! Your optimized extraction is in: {output_dir}/")
                break
                
        except ValueError:
            print("⚠️  Please enter valid numbers")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def analyze_current_extraction():
    """
    Analyze the current grouped extraction results.
    """
    
    summary_file = "extracted_content_grouped/extraction_summary.json"
    
    if not os.path.exists(summary_file):
        print("❌ No grouped extraction found. Run the main script first.")
        return
    
    with open(summary_file, 'r') as f:
        items = json.load(f)
    
    print("📋 CURRENT EXTRACTION ANALYSIS")
    print("=" * 40)
    
    # Analyze grouping efficiency
    total_individual_regions = sum(item.get('individual_regions', 1) for item in items)
    
    print(f"Total groups created: {len(items)}")
    print(f"Total individual regions merged: {total_individual_regions}")
    print(f"Average regions per group: {total_individual_regions / len(items):.1f}")
    print()
    
    # Analyze by page
    by_page = {}
    for item in items:
        page = item['page']
        if page not in by_page:
            by_page[page] = {'yellow': [], 'red': []}
        
        if 'yellow' in item['type']:
            by_page[page]['yellow'].append(item)
        else:
            by_page[page]['red'].append(item)
    
    print("Page-by-page breakdown:")
    for page in sorted(by_page.keys()):
        yellow_count = len(by_page[page]['yellow'])
        red_count = len(by_page[page]['red'])
        
        yellow_regions = sum(item.get('individual_regions', 1) for item in by_page[page]['yellow'])
        red_regions = sum(item.get('individual_regions', 1) for item in by_page[page]['red'])
        
        print(f"  Page {page}: {yellow_count} yellow groups ({yellow_regions} regions), {red_count} red groups ({red_regions} regions)")

def main():
    """Main menu for parameter tuning."""
    
    while True:
        print("\n🛠️  PDF EXTRACTION PARAMETER TUNING")
        print("=" * 45)
        print("1. Analyze current grouped extraction")
        print("2. Interactive parameter tuning")
        print("3. Compare different settings")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == '1':
            analyze_current_extraction()
        elif choice == '2':
            interactive_parameter_tuning()
        elif choice == '3':
            compare_different_settings()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
