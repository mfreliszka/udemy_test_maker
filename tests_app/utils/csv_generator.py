import csv
from io import StringIO
from typing import List, Dict, Any
from django.http import HttpResponse
from ..models import Question, Answer


class UdemyCSVGenerator:
    """
    Utility class to generate CSV files in Udemy format for test creation.
    Based on the CSV template: Question, Question Type, Answer Option 1-6, 
    Explanation 1-6, Correct Answers, Overall Explanation, Domain
    """
    
    HEADERS = [
        'Question',
        'Question Type', 
        'Answer Option 1',
        'Explanation 1',
        'Answer Option 2', 
        'Explanation 2',
        'Answer Option 3',
        'Explanation 3', 
        'Answer Option 4',
        'Explanation 4',
        'Answer Option 5',
        'Explanation 5',
        'Answer Option 6',
        'Explanation 6',
        'Correct Answers',
        'Overall Explanation',
        'Domain'
    ]
    
    def __init__(self):
        self.questions_data = []
    
    def add_question(self, question: Question) -> None:
        """
        Add a question with its answers to the CSV data.
        
        Args:
            question: Question model instance
        """
        answers = question.answers.all().order_by('order')
        
        # Initialize row with question data
        row = {
            'Question': question.question_text,
            'Question Type': self._get_question_type_display(question.question_type),
            'Overall Explanation': question.overall_explanation,
            'Domain': question.domain.name if question.domain else '',
        }
        
        # Add answer options and explanations
        for i in range(6):  # Udemy supports up to 6 answers
            answer_key = f'Answer Option {i + 1}'
            explanation_key = f'Explanation {i + 1}'
            
            if i < len(answers):
                answer = answers[i]
                row[answer_key] = answer.answer_text
                row[explanation_key] = answer.explanation or ''
            else:
                row[answer_key] = ''
                row[explanation_key] = ''
        
        # Generate correct answers string
        correct_answers = []
        for i, answer in enumerate(answers):
            if answer.is_correct:
                correct_answers.append(str(i + 1))
        
        row['Correct Answers'] = ','.join(correct_answers)
        
        self.questions_data.append(row)
    
    def add_questions(self, questions: List[Question]) -> None:
        """
        Add multiple questions to the CSV data.
        
        Args:
            questions: List of Question model instances
        """
        for question in questions:
            self.add_question(question)
    
    def generate_csv_content(self) -> str:
        """
        Generate CSV content as a string.
        
        Returns:
            CSV content as string
        """
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.HEADERS)
        writer.writeheader()
        writer.writerows(self.questions_data)
        return output.getvalue()
    
    def generate_http_response(self, filename: str = 'udemy_test.csv') -> HttpResponse:
        """
        Generate an HTTP response with CSV content for download.
        
        Args:
            filename: Name of the CSV file for download
            
        Returns:
            HttpResponse with CSV content
        """
        response = HttpResponse(
            self.generate_csv_content(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save CSV content to a file.
        
        Args:
            filepath: Path where to save the CSV file
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(self.questions_data)
    
    def clear(self) -> None:
        """Clear all questions data."""
        self.questions_data = []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current CSV data.
        
        Returns:
            Dictionary with statistics
        """
        if not self.questions_data:
            return {
                'total_questions': 0,
                'question_types': {},
                'domains': {},
                'avg_answers_per_question': 0
            }
        
        stats = {
            'total_questions': len(self.questions_data),
            'question_types': {},
            'domains': {},
            'total_answers': 0
        }
        
        for row in self.questions_data:
            # Count question types
            q_type = row['Question Type']
            stats['question_types'][q_type] = stats['question_types'].get(q_type, 0) + 1
            
            # Count domains
            domain = row['Domain']
            stats['domains'][domain] = stats['domains'].get(domain, 0) + 1
            
            # Count non-empty answers
            answer_count = sum(1 for i in range(1, 7) if row[f'Answer Option {i}'])
            stats['total_answers'] += answer_count
        
        stats['avg_answers_per_question'] = round(
            stats['total_answers'] / stats['total_questions'], 2
        ) if stats['total_questions'] > 0 else 0
        
        return stats
    
    @staticmethod
    def _get_question_type_display(question_type: str) -> str:
        """
        Convert internal question type to Udemy format.
        
        Args:
            question_type: Internal question type string
            
        Returns:
            Udemy-compatible question type string
        """
        type_mapping = {
            'multiple_choice': 'multiple-choice',
            'multiple_select': 'multi-select'
        }
        return type_mapping.get(question_type, 'multi-select')


def generate_test_csv(exam_name: str, test_number: int, filename: str = None) -> HttpResponse:
    """
    Convenience function to generate CSV for a specific exam and test number.
    
    Args:
        exam_name: Name of the exam (e.g., 'google_cloud_developer')
        test_number: Test number to filter questions
        filename: Optional filename for the CSV file
        
    Returns:
        HttpResponse with CSV content
    """
    from ..models import Exam
    
    try:
        exam = Exam.objects.get(name=exam_name)
        questions = Question.objects.filter(
            exam=exam, 
            test_number=test_number,
            is_active=True
        ).prefetch_related('answers', 'domain')
        
        if not questions.exists():
            raise ValueError(f"No questions found for {exam.display_name}, Test {test_number}")
        
        generator = UdemyCSVGenerator()
        generator.add_questions(questions)
        
        if not filename:
            filename = f"{exam.slug}_test_{test_number}.csv"
        
        return generator.generate_http_response(filename)
        
    except Exam.DoesNotExist:
        raise ValueError(f"Exam '{exam_name}' not found")


def generate_domain_csv(exam_name: str, domain_name: str, filename: str = None) -> HttpResponse:
    """
    Generate CSV for all questions in a specific domain.
    
    Args:
        exam_name: Name of the exam
        domain_name: Name of the domain
        filename: Optional filename for the CSV file
        
    Returns:
        HttpResponse with CSV content
    """
    from ..models import Exam, Domain
    
    try:
        exam = Exam.objects.get(name=exam_name)
        domain = Domain.objects.get(exam=exam, name=domain_name)
        questions = Question.objects.filter(
            domain=domain,
            is_active=True
        ).prefetch_related('answers')
        
        if not questions.exists():
            raise ValueError(f"No questions found for domain '{domain_name}'")
        
        generator = UdemyCSVGenerator()
        generator.add_questions(questions)
        
        if not filename:
            filename = f"{exam.slug}_{domain.name[:30]}.csv"
        
        return generator.generate_http_response(filename)
        
    except (Exam.DoesNotExist, Domain.DoesNotExist):
        raise ValueError(f"Exam '{exam_name}' or domain '{domain_name}' not found")
