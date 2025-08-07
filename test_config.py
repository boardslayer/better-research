import json
import os

CONFIG_PATH = "config.json"

def load_config(path):
    """Load and validate the JSON config file"""
    try:
        with open(path, "r") as f:
            config = json.load(f)
        print(f"✓ Successfully loaded config from {path}")
        return config
    except FileNotFoundError:
        print(f"✗ Config file not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        return None

def validate_config(config):
    """Validate the config structure and required fields"""
    if config is None:
        return False
    
    print("\n--- Config Validation ---")
    
    # Check required top-level keys
    required_keys = ["ocr_engine", "folders", "extraction"]
    for key in required_keys:
        if key in config:
            print(f"✓ Found required key: {key}")
        else:
            print(f"✗ Missing required key: {key}")
            return False
    
    # Check folders exist or can be created
    folders = config.get("folders", {})
    for folder_type, path in folders.items():
        if os.path.exists(path):
            print(f"✓ Folder exists: {folder_type} -> {path}")
        else:
            print(f"⚠ Folder doesn't exist (will be created): {folder_type} -> {path}")
    
    # Check OCR engine config
    ocr_engine = config.get("ocr_engine")
    if ocr_engine == "mathpix":
        mathpix_config = config.get("mathpix", {})
        if "app_id" in mathpix_config and "app_key" in mathpix_config:
            print("✓ Mathpix configuration found")
        else:
            print("✗ Mathpix configuration incomplete")
            return False
    
    # Check Zotero config if present
    if "zotero" in config:
        zotero_config = config["zotero"]
        required_zotero = ["library_id", "api_key"]
        for key in required_zotero:
            if key in zotero_config:
                print(f"✓ Zotero {key} found")
            else:
                print(f"✗ Zotero {key} missing")
                return False
    
    return True

def test_config_loading():
    """Main test function"""
    print("=== Config File Test ===")
    
    # Load config
    config = load_config(CONFIG_PATH)
    if config is None:
        return False
    
    # Print loaded config structure
    print(f"\n--- Loaded Config Structure ---")
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")
    
    # Validate config
    is_valid = validate_config(config)
    
    print(f"\n--- Test Result ---")
    if is_valid:
        print("✓ Config file is valid and ready to use!")
        return True
    else:
        print("✗ Config file has issues that need to be fixed")
        return False

if __name__ == "__main__":
    success = test_config_loading()
    exit(0 if success else 1)
