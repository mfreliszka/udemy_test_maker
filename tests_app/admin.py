from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Exam, Domain, Question, Answer


class DomainInline(admin.TabularInline):
    """Inline admin for domains within exam admin"""
    model = Domain
    extra = 1
    fields = ['name', 'order', 'weight_percentage', 'is_active']
    ordering = ['order']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'provider', 'total_domains', 'total_questions', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['display_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DomainInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'provider', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_domains(self, obj):
        """Display total number of domains for this exam"""
        count = obj.domains.count()
        url = reverse('admin:tests_app_domain_changelist') + f'?exam__id__exact={obj.id}'
        return format_html('<a href="{}">{} domains</a>', url, count)
    total_domains.short_description = 'Domains'
    
    def total_questions(self, obj):
        """Display total number of questions for this exam"""
        count = obj.questions.count()
        url = reverse('admin:tests_app_question_changelist') + f'?exam__id__exact={obj.id}'
        return format_html('<a href="{}">{} questions</a>', url, count)
    total_questions.short_description = 'Questions'


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam', 'order', 'weight_percentage', 'total_questions', 'is_active']
    list_filter = ['exam', 'is_active']
    search_fields = ['name', 'description', 'exam__display_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['exam', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('exam', 'name', 'description')
        }),
        ('Configuration', {
            'fields': ('order', 'weight_percentage', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_questions(self, obj):
        """Display total number of questions for this domain"""
        count = obj.questions.count()
        url = reverse('admin:tests_app_question_changelist') + f'?domain__id__exact={obj.id}'
        return format_html('<a href="{}">{} questions</a>', url, count)
    total_questions.short_description = 'Questions'


class AnswerInline(admin.TabularInline):
    """Inline admin for answers within question admin"""
    model = Answer
    extra = 1
    fields = ['order', 'answer_text', 'is_correct', 'explanation']
    ordering = ['order']
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
    }


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        'truncated_question', 
        'exam', 
        'domain', 
        'test_number', 
        'question_type',
        'answers_summary',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'exam', 
        'domain', 
        'test_number', 
        'question_type',
        'is_active', 
        'created_at'
    ]
    search_fields = ['question_text', 'overall_explanation', 'exam__display_name', 'domain__name']
    readonly_fields = ['created_at', 'updated_at', 'total_answers', 'correct_answers_count']
    inlines = [AnswerInline]
    
    fieldsets = (
        ('Question Details', {
            'fields': ('exam', 'domain', 'test_number', 'question_type')
        }),
        ('Content', {
            'fields': ('question_text', 'overall_explanation')
        }),
        ('Metadata', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('total_answers', 'correct_answers_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})},
    }
    
    def truncated_question(self, obj):
        """Display truncated question text"""
        return obj.question_text[:75] + "..." if len(obj.question_text) > 75 else obj.question_text
    truncated_question.short_description = 'Question'
    
    def answers_summary(self, obj):
        """Display summary of answers (correct/total)"""
        total = obj.total_answers
        correct = obj.correct_answers_count
        if total == 0:
            return format_html('<span style="color: red;">No answers</span>')
        
        color = 'green' if correct > 0 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} correct</span>',
            color, correct, total
        )
    answers_summary.short_description = 'Answers'
    
    def get_queryset(self, request):
        """Optimize queries by prefetching related objects"""
        return super().get_queryset(request).select_related('exam', 'domain').prefetch_related('answers')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        'truncated_answer', 
        'question_preview', 
        'order', 
        'is_correct_display', 
        'has_explanation',
        'created_at'
    ]
    list_filter = [
        'is_correct', 
        'question__exam', 
        'question__domain', 
        'question__test_number',
        'created_at'
    ]
    search_fields = [
        'answer_text', 
        'explanation', 
        'question__question_text',
        'question__exam__display_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Answer Details', {
            'fields': ('question', 'order', 'is_correct')
        }),
        ('Content', {
            'fields': ('answer_text', 'explanation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 80})},
    }
    
    def truncated_answer(self, obj):
        """Display truncated answer text"""
        return obj.answer_text[:50] + "..." if len(obj.answer_text) > 50 else obj.answer_text
    truncated_answer.short_description = 'Answer'
    
    def question_preview(self, obj):
        """Display preview of the related question"""
        question_text = obj.question.question_text[:40] + "..." if len(obj.question.question_text) > 40 else obj.question.question_text
        url = reverse('admin:tests_app_question_change', args=[obj.question.id])
        return format_html('<a href="{}">{}</a>', url, question_text)
    question_preview.short_description = 'Question'
    
    def is_correct_display(self, obj):
        """Display correct/incorrect with color coding"""
        if obj.is_correct:
            return format_html('<span style="color: green; font-weight: bold;">✓ Correct</span>')
        else:
            return format_html('<span style="color: red;">✗ Incorrect</span>')
    is_correct_display.short_description = 'Status'
    
    def has_explanation(self, obj):
        """Show if answer has explanation"""
        if obj.explanation:
            return format_html('<span style="color: green;">✓</span>')
        else:
            return format_html('<span style="color: orange;">-</span>')
    has_explanation.short_description = 'Explanation'
    
    def get_queryset(self, request):
        """Optimize queries by prefetching related objects"""
        return super().get_queryset(request).select_related('question', 'question__exam', 'question__domain')


# Customize the admin site headers
admin.site.site_header = "Udemy Test Maker Administration"
admin.site.site_title = "Udemy Test Maker Admin"
admin.site.index_title = "Welcome to Udemy Test Maker Administration"