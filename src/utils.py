import json

def load_html(html_path:str):
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()

def save_to_json(data, filename):
    """
    Save data to JSON file with proper Chinese character encoding
    
    Args:
        data (dict): Data to save
        filename (str): Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)