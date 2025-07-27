import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Exam, Domain, Question, Answer


@csrf_exempt
@require_http_methods(["POST"])
def api_create_question(request):
    """
    API endpoint to create a question with answers via POST request.
    
    Expected JSON format:
    {
        "exam": "google_cloud_developer",
        "test_number": 1,
        "question_text": "What is the best practice for...",
        "question_type": "multiple_select",  // or "multiple_choice"
        "overall_explanation": "The correct answers are...",
        "is_active": true,
        "answers": [
            {
                "text": "Answer option 1",
                "is_correct": true,
                "explanation": "This is correct because..."
            },
            {
                "text": "Answer option 2", 
                "is_correct": false,
                "explanation": "This is incorrect because..."
            },
            // ... more answers (3-7 total)
        ]
    }
    """
    
    try:
        # Parse JSON data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Content-Type must be application/json'
            }, status=400)
        
        # Validate required fields
        required_fields = ['exam', 'test_number', 'question_text', 'answers']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        # Validate answers
        answers_data = data.get('answers', [])
        if len(answers_data) < 3:
            return JsonResponse({
                'success': False,
                'error': 'At least 3 answers are required'
            }, status=400)
        
        if len(answers_data) > 7:
            return JsonResponse({
                'success': False,
                'error': 'Maximum 7 answers allowed'
            }, status=400)
        
        # Check if at least one answer is correct
        correct_answers = [answer for answer in answers_data if answer.get('is_correct')]
        if not correct_answers:
            return JsonResponse({
                'success': False,
                'error': 'At least one answer must be marked as correct'
            }, status=400)
        
        # Validate question type and correct answers count
        question_type = data.get('question_type', 'multiple_select')
        if question_type == 'multiple_choice' and len(correct_answers) > 1:
            return JsonResponse({
                'success': False,
                'error': 'Multiple choice questions can only have one correct answer'
            }, status=400)
        
        # Start database transaction
        with transaction.atomic():
            # Get or find exam
            exam_name = data['exam']
            try:
                exam = Exam.objects.get(name=exam_name, is_active=True)
            except Exam.DoesNotExist:
                # Try to find by display name as fallback
                exam = Exam.objects.filter(
                    display_name__icontains=exam_name, 
                    is_active=True
                ).first()
                
                if not exam:
                    return JsonResponse({
                        'success': False,
                        'error': f'Exam "{exam_name}" not found'
                    }, status=404)
            
            domain = None
            domain_name = data.get('domain')
            if domain_name:
                domain = Domain.objects.filter(
                    exam=exam, 
                    name__icontains=domain_name[:50] if len(domain_name) > 50 else domain_name,
                    is_active=True
                ).first()
                
                if not domain:
                    return JsonResponse({
                        'success': False,
                        'error': f'Domain "{domain_name}" not found for exam "{exam.display_name}"',
                        'available_domains': list(exam.domains.filter(is_active=True).values_list('name', flat=True))
                    }, status=404)
            
            # Create question
            question = Question.objects.create(
                exam=exam,
                domain=domain,
                test_number=data['test_number'],
                question_text=data['question_text'],
                question_type=question_type,
                overall_explanation=data.get('overall_explanation', ''),
                is_active=data.get('is_active', True)
            )
            
            # Create answers
            created_answers = []
            for i, answer_data in enumerate(answers_data, 1):
                if not answer_data.get('text'):
                    continue
                    
                answer = Answer.objects.create(
                    question=question,
                    answer_text=answer_data['text'],
                    is_correct=answer_data.get('is_correct', False),
                    explanation=answer_data.get('explanation', ''),
                    order=i
                )
                created_answers.append({
                    'id': answer.id,
                    'text': answer.answer_text,
                    'is_correct': answer.is_correct,
                    'explanation': answer.explanation,
                    'order': answer.order
                })
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Question created successfully',
                'data': {
                    'question_id': question.id,
                    'exam': exam.display_name,
                    'domain': domain.name if domain else None,
                    'test_number': question.test_number,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'total_answers': len(created_answers),
                    'correct_answers': len([a for a in created_answers if a['is_correct']]),
                    'answers': created_answers,
                    'view_url': f'/questions/{question.id}/',
                    'edit_url': f'/questions/{question.id}/edit/'
                }
            }, status=201)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)


@csrf_exempt  
@require_http_methods(["GET"])
def api_get_exams_and_domains(request):
    """
    API endpoint to get available exams and their domains.
    Useful for Chrome extension to know what exams/domains are available.
    """
    
    try:
        exams_data = []
        exams = Exam.objects.filter(is_active=True).prefetch_related('domains')
        
        for exam in exams:
            domains = list(exam.domains.filter(is_active=True).values('id', 'name', 'order'))
            exams_data.append({
                'id': exam.id,
                'name': exam.name,
                'display_name': exam.display_name,
                'provider': exam.provider,
                'domains': domains
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'exams': exams_data,
                'total_exams': len(exams_data)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error fetching exams: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_question_stats(request):
    """
    API endpoint to get statistics about questions.
    Useful for monitoring the Chrome extension's activity.
    """
    
    try:
        from django.db.models import Count, Q
        
        stats = {
            'total_questions': Question.objects.filter(is_active=True).count(),
            'total_answers': Answer.objects.count(),
            'by_exam': {},
            'by_type': {},
            'recent_questions': []
        }
        
        # Questions by exam
        exam_stats = Question.objects.filter(is_active=True).values(
            'exam__display_name'
        ).annotate(count=Count('id')).order_by('-count')
        
        for stat in exam_stats:
            stats['by_exam'][stat['exam__display_name']] = stat['count']

        # Questions by type
        type_stats = Question.objects.filter(is_active=True).values(
            'question_type'
        ).annotate(count=Count('id'))
        
        for stat in type_stats:
            stats['by_type'][stat['question_type']] = stat['count']
        
        # Recent questions (last 10)
        recent = Question.objects.filter(is_active=True).select_related(
            'exam', 'domain'
        ).order_by('-created_at')[:10]
        
        for question in recent:
            stats['recent_questions'].append({
                'id': question.id,
                'text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                'exam': question.exam.display_name,
                'test_number': question.test_number,
                'created_at': question.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error fetching stats: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_suggest_domains(request):
    """
    API endpoint to get domain suggestions based on question text.
    
    Expected JSON format:
    {
        "question_text": "Your question here...",
        "exam_id": 1
    }
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Content-Type must be application/json'
            }, status=400)
        
        question_text = data.get('question_text', '').strip()
        exam_id = data.get('exam_id')
        
        if not question_text:
            return JsonResponse({
                'success': False,
                'error': 'Question text is required'
            }, status=400)
        if not exam_id:
            return JsonResponse({
                'success': False,
                'error': 'Exam ID is required'
            }, status=400)
        
        # Get domain suggestions
        from .utils.domain_suggester import DomainSuggester
        suggester = DomainSuggester()
        suggestions = suggester.get_domain_suggestions_for_exam(question_text, exam_id)
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions,
            'total_suggestions': len(suggestions)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating suggestions: {str(e)}'
        }, status=500)
