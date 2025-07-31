#!/usr/bin/env python3
"""
HTML to Udemy CSV Converter
Extracts quiz questions from HTML and converts to Udemy-compatible CSV format
"""

import csv
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove HTML entities
    text = text.replace('&nbsp;', ' ')
    return text

def extract_links_and_images(soup_element):
    """Extract all links and images from explanation"""
    links = []
    images = []
    
    # Extract all links
    for link in soup_element.find_all('a', href=True):
        url = link.get('href')
        link_text = clean_text(link.get_text())
        if url:
            links.append(f"{link_text}: {url}" if link_text else url)
    
    # Extract all images
    for img in soup_element.find_all('img', src=True):
        src = img.get('src')
        alt = img.get('alt', '')
        if src:
            images.append(f"Image{' (' + alt + ')' if alt else ''}: {src}")
    
    return links, images

def determine_correct_answers(question_element, question_type):
    """Determine correct answers based on question type"""
    correct_answers = []
    
    if question_type == "multiple-choice":
        # For single choice, find the answer marked with wpProQuiz_answerCorrect
        answer_items = question_element.find_all('li', class_='wpProQuiz_questionListItem')
        for item in answer_items:
            # Check if this item has the correct answer class
            classes = item.get('class', [])
            if 'wpProQuiz_answerCorrect' in classes:
                pos = item.get('data-pos')
                if pos is not None:
                    # Convert to number (0=1, 1=2, etc.)
                    correct_answers.append(str(int(pos) + 1))
                    break  # Only one correct answer for single choice
    
    elif question_type == "multi-select":
        # For multiple choice, extract from explanation text
        explanation_div = question_element.find('div', class_='wpProQuiz_response')
        if explanation_div:
            explanation_text = explanation_div.get_text()
            
            # Look for "Correct answers: A, C" pattern - be more precise
            patterns = [
                r'Correct answers?:\s*([A-Z](?:\s*,\s*[A-Z])*)',  # Matches "A, C" but stops before other text
                r'Correct answers?:\s*([A-Z](?:\s+and\s+[A-Z])*)',  # Matches "A and C"
                r'Correct answers?:\s*([A-Z](?:\s*[A-Z])*)'  # Matches "A C"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, explanation_text, re.IGNORECASE)
                if match:
                    answers_str = match.group(1)
                    print(f"Debug: Found answers string: '{answers_str}'")
                    # Extract only the letters (A, B, C, etc.)
                    letters = re.findall(r'[A-Z]', answers_str.upper())
                    print(f"Debug: Extracted letters: {letters}")
                    for letter in letters:
                        # Convert A=1, B=2, C=3, etc.
                        number = str(ord(letter) - ord('A') + 1)
                        if number not in correct_answers:  # Avoid duplicates
                            correct_answers.append(number)
                    if correct_answers:  # If we found answers, stop looking
                        break
        
        # Ensure multi-select has at least 2 correct answers
        if len(correct_answers) < 2:
            print(f"Warning: Multi-select question has only {len(correct_answers)} correct answer(s). Adding default second answer.")
            if len(correct_answers) == 0:
                correct_answers = ["1", "2"]  # Default to first two options
            elif len(correct_answers) == 1:
                # Add a second answer (different from the first)
                existing = int(correct_answers[0])
                if existing == 1:
                    correct_answers.append("2")
                else:
                    correct_answers.append("1")
    
    print(f"Debug: Final correct answers: {correct_answers}")
    return correct_answers

def extract_question_data(question_element):
    """Extract all data from a single question element"""
    data = {
        'question': '',
        'question_type': '',
        'answers': [],
        'explanations': [],
        'correct_answers': [],
        'overall_explanation': '',
        'domain': ''
    }
    
    # Extract question text
    question_text_div = question_element.find('div', class_='wpProQuiz_question_text')
    if question_text_div:
        data['question'] = clean_text(question_text_div.get_text())
    
    # Determine question type
    question_list = question_element.find('ul', class_='wpProQuiz_questionList')
    if question_list:
        data_type = question_list.get('data-type', '')
        if data_type == 'single':
            data['question_type'] = 'multiple-choice'
        elif data_type == 'multiple':
            data['question_type'] = 'multi-select'
    
    # Extract answers
    answer_items = question_element.find_all('li', class_='wpProQuiz_questionListItem')
    for item in answer_items:
        label = item.find('label')
        if label:
            # Remove the input element and get clean text
            input_elem = label.find('input')
            if input_elem:
                input_elem.decompose()
            answer_text = clean_text(label.get_text())
            data['answers'].append(answer_text)
            # For now, we'll add empty explanations - you can modify this if answer-specific explanations exist
            data['explanations'].append('')
    
    # Determine correct answers
    data['correct_answers'] = determine_correct_answers(question_element, data['question_type'])
    
    # Validate correct answers based on question type
    if not data['correct_answers']:
        print(f"Warning: No correct answers found for question. Setting default.")
        if data['question_type'] == 'multi-select':
            data['correct_answers'] = ['1', '2']  # Default for multi-select
        else:
            data['correct_answers'] = ['1']  # Default for single choice
    elif data['question_type'] == 'multi-select' and len(data['correct_answers']) < 2:
        print(f"Warning: Multi-select question has only {len(data['correct_answers'])} correct answer. Adding second answer.")
        existing = data['correct_answers'][0]
        if existing == '1':
            data['correct_answers'].append('2')
        else:
            data['correct_answers'].append('1')
    
    # Extract overall explanation
    explanation_div = question_element.find('div', class_='wpProQuiz_response')
    if explanation_div:
        # Get the main explanation text
        explanation_paragraphs = explanation_div.find_all('p')
        explanation_parts = []
        
        for p in explanation_paragraphs:
            # Extract links and images from this paragraph
            links, images = extract_links_and_images(p)
            
            # Get clean text content
            text_content = clean_text(p.get_text())
            if text_content:
                explanation_parts.append(text_content)
            
            # Add images
            for img in images:
                explanation_parts.append(img)
            
            # Add links
            for link in links:
                explanation_parts.append(link)
        
        data['overall_explanation'] = ' | '.join(explanation_parts)
    
    return data

def convert_html_to_csv(input_file_path, output_file_path=None):
    """Convert HTML quiz file to Udemy CSV format"""
    
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found.")
        return
    
    # Set default output file path
    if output_file_path is None:
        base_name = os.path.splitext(input_file_path)[0]
        output_file_path = f"{base_name}_udemy_questions.csv"
    
    # Read and parse HTML
    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all question items
    question_items = soup.find_all('li', class_='wpProQuiz_listItem')
    
    print(f"Found {len(question_items)} questions in the HTML file.")
    
    # Extract data from each question
    questions_data = []
    for i, item in enumerate(question_items, 1):
        print(f"Processing question {i}...")
        question_data = extract_question_data(item)
        if question_data['question']:  # Only add if we found a question
            print(f"  - Type: {question_data['question_type']}")
            print(f"  - Answers: {len(question_data['answers'])} options")
            print(f"  - Correct: {question_data['correct_answers']}")
            questions_data.append(question_data)
        else:
            print(f"  - Skipped (no question text found)")
    
    # Write to CSV
    fieldnames = [
        'Question', 'Question Type',
        'Answer Option 1', 'Explanation 1',
        'Answer Option 2', 'Explanation 2',
        'Answer Option 3', 'Explanation 3',
        'Answer Option 4', 'Explanation 4',
        'Answer Option 5', 'Explanation 5',
        'Answer Option 6', 'Explanation 6',
        'Correct Answers', 'Overall Explanation', 'Domain'
    ]
    
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for question_data in questions_data:
            row = {
                'Question': question_data['question'],
                'Question Type': question_data['question_type'],
                'Correct Answers': ','.join(question_data['correct_answers']) if question_data['correct_answers'] else '1',
                'Overall Explanation': question_data['overall_explanation'],
                'Domain': question_data['domain']  # You can set this manually or extract from context
            }
            
            # Add answers and explanations (up to 6)
            for i in range(6):
                answer_key = f'Answer Option {i+1}'
                explanation_key = f'Explanation {i+1}'
                
                if i < len(question_data['answers']):
                    row[answer_key] = question_data['answers'][i]
                    row[explanation_key] = question_data['explanations'][i] if i < len(question_data['explanations']) else ''
                else:
                    row[answer_key] = ''
                    row[explanation_key] = ''
            
            writer.writerow(row)
    
    print(f"Successfully converted {len(questions_data)} questions to '{output_file_path}'")
    return output_file_path

def main():
    """Main function to run the converter"""
    print("HTML to Udemy CSV Converter")
    print("=" * 50)
    
    # Get input file path from user
    input_path = input("Enter the path to the HTML file: ").strip()
    
    # Remove quotes if present
    input_path = input_path.strip('"\'')
    
    # Ask for output path (optional)
    output_path = input("Enter output CSV file path (press Enter for auto-generated name): ").strip()
    if not output_path:
        output_path = None
    
    try:
        result_path = convert_html_to_csv(input_path, output_path)
        if result_path:
            print(f"\nConversion completed successfully!")
            print(f"Output file: {result_path}")
            
            # Ask if user wants to see a preview
            preview = input("\nWould you like to see a preview of the first question? (y/n): ").lower()
            if preview == 'y':
                with open(result_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    first_row = next(reader, None)
                    if first_row:
                        print("\nFirst question preview:")
                        print("-" * 30)
                        for key, value in first_row.items():
                            if value:  # Only show non-empty fields
                                print(f"{key}: {value}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()