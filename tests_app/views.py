from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Exam, Domain, Question, Answer
from .utils.csv_generator import UdemyCSVGenerator, generate_test_csv


def dashboard(request):
    """Main dashboard view for the Udemy Test Maker app."""
    
    # Get statistics for the dashboard
    stats = {
        'total_exams': Exam.objects.filter(is_active=True).count(),
        'total_questions': Question.objects.filter(is_active=True).count(),
        'total_domains': Domain.objects.filter(is_active=True).count(),
        'total_answers': Answer.objects.count(),
    }
    
    # Get recent questions
    recent_questions = Question.objects.filter(
        is_active=True
    ).select_related(
        'exam', 'domain'
    ).prefetch_related(
        'answers'
    ).order_by('-created_at')[:5]
    
    # Get exams with question counts
    exams_with_counts = Exam.objects.filter(
        is_active=True
    ).annotate(
        question_count=Count('questions', filter=Q(questions__is_active=True)),
        domain_count=Count('domains', filter=Q(domains__is_active=True))
    ).order_by('provider', 'display_name')
    
    context = {
        'title': 'Udemy Test Maker Dashboard',
        'stats': stats,
        'recent_questions': recent_questions,
        'exams': exams_with_counts,
    }
    return render(request, 'tests_app/dashboard.html', context)


def question_list(request):
    """List all questions with filtering and search capabilities."""
    
    questions = Question.objects.filter(
        is_active=True
    ).select_related(
        'exam', 'domain'
    ).prefetch_related(
        'answers'
    ).order_by('-created_at')
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    exam_filter = request.GET.get('exam', '')
    test_filter = request.GET.get('test', '')
    type_filter = request.GET.get('type', '')
    
    # Apply filters
    if search_query:
        questions = questions.filter(
            Q(question_text__icontains=search_query) |
            Q(exam__display_name__icontains=search_query) |
            Q(domain__name__icontains=search_query)
        )
    
    if exam_filter:
        questions = questions.filter(exam__name=exam_filter)
    
    if test_filter:
        questions = questions.filter(test_number=test_filter)
    
    if type_filter:
        questions = questions.filter(question_type=type_filter)
    
    # Pagination
    paginator = Paginator(questions, 10)  # Show 10 questions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all exams for filter dropdown
    exams = Exam.objects.filter(is_active=True)
    
    context = {
        'questions': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'exams': exams,
        'total_count': paginator.count,
        'search_query': search_query,
        'current_filters': {
            'exam': exam_filter,
            'test': test_filter,
            'type': type_filter,
        }
    }
    return render(request, 'tests_app/question_list.html', context)


def question_detail(request, pk):
    """Display detailed view of a single question."""
    
    question = get_object_or_404(
        Question.objects.select_related('exam', 'domain').prefetch_related('answers'),
        pk=pk
    )
    
    # Get answers ordered by their order field
    answers = question.answers.all().order_by('order')
    
    # Get related questions (same exam and test number)
    related_questions = Question.objects.filter(
        exam=question.exam,
        test_number=question.test_number,
        is_active=True
    ).exclude(pk=question.pk).select_related('exam', 'domain')[:5]
    
    # Get previous and next questions for navigation
    previous_question = Question.objects.filter(
        exam=question.exam,
        test_number=question.test_number,
        pk__lt=question.pk,
        is_active=True
    ).order_by('-pk').first()
    
    next_question = Question.objects.filter(
        exam=question.exam,
        test_number=question.test_number,
        pk__gt=question.pk,
        is_active=True
    ).order_by('pk').first()
    
    context = {
        'question': question,
        'answers': answers,
        'related_questions': related_questions,
        'previous_question': previous_question,
        'next_question': next_question,
    }
    return render(request, 'tests_app/question_detail.html', context)


def question_add(request):
    """Add a new question."""
    
    if request.method == 'POST':
        return handle_question_form(request)
    
    # Get all exams for the form
    exams = Exam.objects.filter(is_active=True).prefetch_related('domains')
    
    context = {
        'exams': exams,
        'question': None,  # Indicates this is a new question
    }
    return render(request, 'tests_app/question_form.html', context)


def question_edit(request, pk):
    """Edit an existing question."""
    
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        return handle_question_form(request, question)
    
    # Get all exams for the form
    exams = Exam.objects.filter(is_active=True).prefetch_related('domains')
    
    context = {
        'exams': exams,
        'question': question,
    }
    return render(request, 'tests_app/question_form.html', context)


def handle_question_form(request, question=None):
    """Handle question form submission (both add and edit)."""
    
    try:
        # Get form data
        exam_id = request.POST.get('exam')
        domain_id = request.POST.get('domain')
        test_number = request.POST.get('test_number')
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        overall_explanation = request.POST.get('overall_explanation', '')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validate required fields
        if not all([exam_id, test_number, question_text, question_type]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('tests_app:question_add' if not question else 'tests_app:question_edit', pk=question.pk if question else None)
        
        # Get related objects
        exam = get_object_or_404(Exam, pk=exam_id)
        domain = None
        if domain_id:
            domain = get_object_or_404(Domain, pk=domain_id)
        
        # Create or update question
        if question:
            question.exam = exam
            question.domain = domain
            question.test_number = int(test_number)
            question.question_text = question_text
            question.question_type = question_type
            question.overall_explanation = overall_explanation
            question.is_active = is_active
            question.save()
            
            # Delete existing answers
            question.answers.all().delete()
            action = 'updated'
        else:
            question = Question.objects.create(
                exam=exam,
                domain=domain,
                test_number=int(test_number),
                question_text=question_text,
                question_type=question_type,
                overall_explanation=overall_explanation,
                is_active=is_active
            )
            action = 'created'
        
        # Process answers
        answer_count = 0
        has_correct_answer = False
        
        # Find all answer fields
        for key in request.POST.keys():
            if key.startswith('answer_') and key.endswith('_text'):
                # Extract answer index
                answer_index = key.split('_')[1]
                
                answer_text = request.POST.get(f'answer_{answer_index}_text', '').strip()
                if not answer_text:
                    continue
                
                is_correct = request.POST.get(f'answer_{answer_index}_correct') == 'on'
                explanation = request.POST.get(f'answer_{answer_index}_explanation', '').strip()
                
                answer_count += 1
                if is_correct:
                    has_correct_answer = True
                
                Answer.objects.create(
                    question=question,
                    answer_text=answer_text,
                    is_correct=is_correct,
                    explanation=explanation,
                    order=answer_count
                )
        
        # Validate answers
        if answer_count < 3:
            messages.error(request, 'Please provide at least 3 answer options.')
            question.delete() if action == 'created' else None
            return redirect('tests_app:question_add' if not question else 'tests_app:question_edit', pk=question.pk if question else None)
        
        if not has_correct_answer:
            messages.error(request, 'Please mark at least one answer as correct.')
            question.delete() if action == 'created' else None
            return redirect('tests_app:question_add' if not question else 'tests_app:question_edit', pk=question.pk if question else None)
        
        messages.success(request, f'Question {action} successfully!')
        return redirect('tests_app:question_detail', pk=question.pk)
        
    except Exception as e:
        messages.error(request, f'Error saving question: {str(e)}')
        return redirect('tests_app:question_add' if not question else 'tests_app:question_edit', pk=question.pk if question else None)


def question_delete(request, pk):
    """Delete a question."""
    
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        question_text = question.question_text[:50]
        question.delete()
        messages.success(request, f'Question "{question_text}..." has been deleted.')
        return redirect('tests_app:question_list')
    
    context = {
        'question': question,
    }
    return render(request, 'tests_app/question_confirm_delete.html', context)


def question_duplicate(request, pk):
    """Duplicate a question."""
    
    original_question = get_object_or_404(Question, pk=pk)
    
    # Create a duplicate question
    new_question = Question.objects.create(
        exam=original_question.exam,
        domain=original_question.domain,
        test_number=original_question.test_number,
        question_text=f"[COPY] {original_question.question_text}",
        question_type=original_question.question_type,
        difficulty=original_question.difficulty,
        overall_explanation=original_question.overall_explanation,
        created_by=original_question.created_by,
        is_active=False  # Set as inactive by default
    )
    
    # Duplicate answers
    for answer in original_question.answers.all():
        Answer.objects.create(
            question=new_question,
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
            explanation=answer.explanation,
            order=answer.order
        )
    
    messages.success(request, 'Question duplicated successfully. Please review and edit as needed.')
    return redirect('tests_app:question_edit', pk=new_question.pk)


@require_http_methods(["GET"])
def export_question_csv(request, pk):
    """Export a single question as CSV."""
    
    question = get_object_or_404(Question, pk=pk)
    
    generator = UdemyCSVGenerator()
    generator.add_question(question)
    
    filename = f"question_{question.pk}_{question.exam.slug}.csv"
    return generator.generate_http_response(filename)


# @require_http_methods(["GET"])
# def export_test_csv(request):
#     """Export questions for a specific test as CSV."""
    
#     exam_name = request.GET.get('exam')
#     test_number = request.GET.get('test')
    
#     if not exam_name or not test_number:
#         messages.error(request, 'Please specify both exam and test number.')
#         return redirect('tests_app:dashboard')
    
#     try:
#         return generate_test_csv(exam_name, int(test_number))
#     except ValueError as e:
#         messages.error(request, str(e))
#         return redirect('tests_app:dashboard')
#     except Exception as e:
#         messages.error(request, f'Error generating CSV: {str(e)}')
#         return redirect('tests_app:dashboard')
@require_http_methods(["GET"])
def export_test_csv(request):
    """Export questions for a specific test as CSV."""
    
    exam_name = request.GET.get('exam')
    test_number = request.GET.get('test')
    
    print(f"Export request: exam={exam_name}, test={test_number}")  # Debug log
    
    if not exam_name or not test_number:
        messages.error(request, 'Please specify both exam and test number.')
        return redirect('tests_app:dashboard')
    
    try:
        # Add debug logging
        from .models import Question
        questions = Question.objects.filter(
            exam__name=exam_name, 
            test_number=int(test_number),
            is_active=True
        )
        print(f"Found {questions.count()} questions to export")  # Debug log
        
        response = generate_test_csv(exam_name, int(test_number))
        print("CSV generated successfully")  # Debug log
        return response
        
    except ValueError as e:
        print(f"ValueError: {e}")  # Debug log
        messages.error(request, str(e))
        return redirect('tests_app:dashboard')
    except Exception as e:
        print(f"Exception: {e}")  # Debug log
        messages.error(request, f'Error generating CSV: {str(e)}')
        return redirect('tests_app:dashboard')


@csrf_exempt
def ajax_load_domains(request):
    """AJAX endpoint to load domains for a specific exam."""
    
    exam_id = request.GET.get('exam_id')
    if not exam_id:
        return JsonResponse({'domains': []})
    
    try:
        exam = Exam.objects.get(pk=exam_id, is_active=True)
        domains = list(exam.domains.filter(is_active=True).values('id', 'name'))
        return JsonResponse({'domains': domains})
    except Exam.DoesNotExist:
        return JsonResponse({'domains': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)