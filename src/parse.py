import warnings
warnings.filterwarnings('ignore')

import os
from bs4 import BeautifulSoup

from tqdm import tqdm

from utils import *


OUTPUT_ROOT = "../output"
OUTPUT_HTML_ROOT = f"{OUTPUT_ROOT}/html"
OUTPUT_JSON_ROOT = f"{OUTPUT_ROOT}/json"


def parse_idiom_page(html_content):
    """
    Parse Chinese idiom page HTML content and return structured data
    
    Args:
        html_content (str): HTML content of the idiom page
        
    Returns:
        dict: Structured idiom data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize the result dictionary
    idiom_data = {
        "title": "",
        "pronunciation": {
            "zhuyin": {
                "characters": []
            },
            "pinyin": ""
        },
        "definition": "",
        "etymology": {
            "explanation": "",
            "story": ""
        },
        "usage": {
            "semantic": "",
            "category": "",
            "examples": []
        },
        "related_terms": {
            "synonyms": [],
            "reference_words": []
        }
    }
    
    # Get title
    title_element = soup.find('h2')
    if title_element:
        idiom_data["title"] = title_element.text.strip()
    
    # Find all sections by their h3 headers
    sections = soup.find_all('h3')
    
    for section in sections:
        section_title = section.text.strip()
        section_content = section.find_next()
        
        if section_title == "音讀與釋義":
            # Get the div container first
            row_mean = section.find_next('div', id='row_mean')
            if row_mean:
                # Parse pronunciation - directly find h4 within row_mean
                zhuyin_elements = row_mean.find('h4', class_='ti', text='注　　音').find_next_siblings('nbr')
                if zhuyin_elements:
                    idiom_data["pronunciation"]["zhuyin"]["characters"] = [elem.text.strip() for elem in zhuyin_elements]
                
                # Parse pinyin - directly find h4 within row_mean
                pinyin_header = row_mean.find('h4', class_='ti', text='漢語拼音')
                if pinyin_header:
                    pinyin_text = pinyin_header.find_next_sibling(string=True)
                    if pinyin_text:
                        idiom_data["pronunciation"]["pinyin"] = pinyin_text.strip()
                
                # Parse definition - directly find h4 within row_mean
                definition_header = row_mean.find('h4', class_='ti', text='釋　　義')
                if definition_header:
                    definition_text = definition_header.find_next_sibling(string=True)
                    if definition_text:
                        idiom_data["definition"] = definition_text.strip()
        
        elif section_title == "典故說明":
            if section_content:
                idiom_data["etymology"]["story"] = section_content.text.strip()
        
        elif section_title == "用法說明":
            # Parse semantic meaning
            semantic_header = section_content.find_next('h4', text='語義說明')
            if semantic_header:
                semantic_text = semantic_header.find_next_sibling(string=True)
                if semantic_text:
                    idiom_data["usage"]["semantic"] = semantic_text.strip()
            
            # Parse category
            category_header = section_content.find_next('h4', text='使用類別')
            if category_header:
                category_text = category_header.find_next_sibling(string=True)
                if category_text:
                    idiom_data["usage"]["category"] = category_text.strip()
            
            # Parse examples
            examples = section_content.find_all('li')
            idiom_data["usage"]["examples"] = [example.text.strip() for example in examples]
        
        elif section_title == "辨　　識":
            # Parse synonyms
            synonyms_div = section_content.find('h4', text='近義')
            if synonyms_div:
                synonyms_text = synonyms_div.find_next_sibling(string=True)
                if synonyms_text:
                    idiom_data["related_terms"]["synonyms"] = [s.strip() for s in synonyms_text.split('」') if s.strip()]
        
        elif section_title == "參考詞語":
            reference_words = []
            for ref_term in section_content.find_all('li'):
                word_data = {
                    "term": "",
                    "pronunciation": {
                        "zhuyin": [],
                        "pinyin": ""
                    },
                    "definition": ""
                }
                
                # Get term name
                term_div = ref_term.find('div')
                if term_div:
                    word_data["term"] = term_div.text.strip()
                
                # Get pronunciation
                zhuyin_elements = ref_term.find_all('nbr')
                word_data["pronunciation"]["zhuyin"] = [elem.text.strip() for elem in zhuyin_elements]
                
                pinyin_header = ref_term.find('h4', text='漢語拼音')
                if pinyin_header:
                    pinyin_text = pinyin_header.find_next_sibling(string=True)
                    if pinyin_text:
                        word_data["pronunciation"]["pinyin"] = pinyin_text.strip()
                
                # Get definition
                definition_header = ref_term.find('h4', text='釋　　義')
                if definition_header:
                    definition_text = definition_header.find_next_sibling(string=True)
                    if definition_text:
                        word_data["definition"] = definition_text.strip()
                
                reference_words.append(word_data)
            
            idiom_data["related_terms"]["reference_words"] = reference_words
    
    return idiom_data


def main():

    if OUTPUT_JSON_ROOT and not os.path.exists(OUTPUT_JSON_ROOT):
        os.makedirs(OUTPUT_JSON_ROOT, exist_ok=True)

    html_list = sorted(os.listdir(OUTPUT_HTML_ROOT))

    for i in tqdm(range(len(html_list))):

        html_path = html_list[i]

        json_filename = html_path.replace('.html', '.json')

        html_path = os.path.join(OUTPUT_HTML_ROOT, html_path)
        html_content = load_html(html_path)

        if not html_content:
            continue

        idiom_data = parse_idiom_page(html_content)

        output_json_path = f"{OUTPUT_JSON_ROOT}/{json_filename}"
        save_to_json(idiom_data, output_json_path)


if __name__ == '__main__':
    main()