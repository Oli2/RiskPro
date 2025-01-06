import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import logging
from pathlib import Path
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Process SEC EDGAR documents for LLM analysis.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL of the SEC EDGAR document to process'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='processed_document.txt',
        help='Output file path for the processed document'
    )
    
    return parser.parse_args()

def fetch_document(url: str) -> str:
    """Fetch SEC document from URL."""
    headers = {
        'User-Agent': 'tcheckiewicz@gmail.com',  # Replace with your details
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch document: {e}")
        raise

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:?!()\-\'\"$%]', '', text)
    return text.strip()

def extract_sections(soup: BeautifulSoup) -> List[Dict]:
    """Extract document sections maintaining hierarchy."""
    sections = []
    
    # Find all potential section elements
    content = soup.find('div', {'class': 'registrationContent'}) or soup.body
    
    if not content:
        logger.warning("Could not find main content container")
        return sections

    for element in content.find_all(['p', 'table', 'h1', 'h2', 'h3', 'h4', 'div']):
        if element.name == 'table':
            processed_content = process_table(element)
            if processed_content:
                sections.append({
                    'type': 'table',
                    'content': processed_content
                })
        else:
            text = clean_text(element.get_text())
            if text:
                section_type = 'heading' if element.name.startswith('h') else 'paragraph'
                sections.append({
                    'type': section_type,
                    'content': text
                })
    
    return sections

def process_table(table) -> str:
    """Process HTML table into formatted text."""
    rows = []
    
    # Process headers
    headers = []
    for th in table.find_all('th'):
        headers.append(clean_text(th.get_text()))
    if headers:
        rows.append(" | ".join(headers))
        rows.append("-" * len(rows[0]))  # Add separator line
    
    # Process rows
    for tr in table.find_all('tr'):
        cells = []
        for td in tr.find_all('td'):
            cells.append(clean_text(td.get_text()))
        if cells:
            rows.append(" | ".join(cells))
    
    return "\n".join(rows)

def format_for_llm(sections: List[Dict]) -> str:
    """Format content for LLM processing."""
    formatted_text = []
    
    for section in sections:
        if section['type'] == 'heading':
            formatted_text.append(f"\n### {section['content']}\n")
        elif section['type'] == 'table':
            formatted_text.append(f"\n```\n{section['content']}\n```\n")
        else:
            formatted_text.append(section['content'])
    
    return "\n\n".join(formatted_text)

def main(url: str, output_file: str = "processed_document.txt"):
    try:
        # Fetch and parse document
        html_content = fetch_document(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract and process sections
        sections = extract_sections(soup)
        
        # Format for LLM
        formatted_text = format_for_llm(sections)
        
        # Save to file
        output_path = Path(output_file)
        output_path.write_text(formatted_text, encoding='utf-8')
        
        logger.info(f"Document processed and saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise

if __name__ == "__main__":
    args = parse_arguments()
    main(args.url, args.output) 