from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Exam(models.Model):
    """Model representing different certification exams"""
    
    # Predefined exam choices
    GOOGLE_CLOUD_DEVELOPER = 'google_cloud_developer'
    GOOGLE_CLOUD_ARCHITECT = 'google_cloud_architect'
    GOOGLE_CLOUD_ENGINEER = 'google_cloud_engineer'
    GOOGLE_CLOUD_SECURITY = 'google_cloud_security'
    GOOGLE_CLOUD_DATA_ENGINEER = 'google_cloud_data_engineer'
    GOOGLE_CLOUD_DEVOPS = 'google_cloud_devops'
    AWS_SOLUTIONS_ARCHITECT = 'aws_solutions_architect'
    AWS_DEVELOPER = 'aws_developer'
    AWS_SYSOPS = 'aws_sysops'
    
    EXAM_CHOICES = [
        (GOOGLE_CLOUD_DEVELOPER, 'Google Professional Cloud Developer'),
        (GOOGLE_CLOUD_ARCHITECT, 'Google Professional Cloud Architect'),
        (GOOGLE_CLOUD_ENGINEER, 'Google Cloud Associate Engineer'),
        (GOOGLE_CLOUD_SECURITY, 'Google Professional Cloud Security Engineer'),
        (GOOGLE_CLOUD_DATA_ENGINEER, 'Google Professional Data Engineer'),
        (GOOGLE_CLOUD_DEVOPS, 'Google Professional Cloud DevOps Engineer'),
        (AWS_SOLUTIONS_ARCHITECT, 'AWS Certified Solutions Architect'),
        (AWS_DEVELOPER, 'AWS Certified Developer'),
        (AWS_SYSOPS, 'AWS Certified SysOps Administrator'),
    ]
    
    name = models.CharField(max_length=100, choices=EXAM_CHOICES, unique=True)
    display_name = models.CharField(max_length=200, help_text="Full display name of the exam")
    description = models.TextField(blank=True, help_text="Description of the exam content and objectives")
    provider = models.CharField(max_length=50, default='Google Cloud', help_text="Certification provider (Google Cloud, AWS, etc.)")
    is_active = models.BooleanField(default=True, help_text="Whether this exam is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['provider', 'display_name']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
    
    def __str__(self):
        return self.display_name
    
    @property
    def slug(self):
        return slugify(self.display_name)


class Domain(models.Model):
    """Model representing exam domains/sections"""
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='domains')
    name = models.CharField(max_length=200, help_text="Domain name (e.g., 'Section 1: Designing applications')")
    description = models.TextField(blank=True, help_text="Detailed description of the domain content")
    order = models.PositiveIntegerField(default=1, help_text="Order of the domain in the exam")
    weight_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage weight of this domain in the exam (0-100%)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['exam', 'order', 'name']
        unique_together = ['exam', 'name']
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
    
    def __str__(self):
        return f"{self.exam.display_name} - {self.name}"


class Question(models.Model):
    """Model representing exam questions"""
    
    # Question type choices
    MULTIPLE_CHOICE = 'multiple_choice'
    MULTIPLE_SELECT = 'multiple_select'
    
    QUESTION_TYPE_CHOICES = [
        (MULTIPLE_SELECT, 'Multiple Select (default)'),
        (MULTIPLE_CHOICE, 'Multiple Choice (single answer)'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='questions', blank=True, null=True)
    test_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Test number (typically 1-15, up to 50 for flexibility)"
    )
    
    question_text = models.TextField(help_text="The main question text")
    question_type = models.CharField(
        max_length=20, 
        choices=QUESTION_TYPE_CHOICES, 
        default=MULTIPLE_SELECT,
        help_text="Type of question (multiple choice or multiple select)"
    )
    
    overall_explanation = models.TextField(
        blank=True,
        help_text="Overall explanation for the question (why the correct answers are correct)"
    )

    image_external_url = models.ImageField(
        blank=True,
        help_text="Image related to the question (optional)"
    )

    image_external_url = models.URLField(
        blank=True,
        help_text="URL of an image related to the question (optional)"
    )
    # Metadata fields
    is_active = models.BooleanField(default=True, help_text="Whether this question is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['exam', 'test_number', 'domain', 'id']
        indexes = [
            models.Index(fields=['exam', 'test_number']),
            models.Index(fields=['domain']),
            models.Index(fields=['question_type']),
        ]
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return f"Test {self.test_number} - {self.question_text[:50]}..."
    
    @property
    def correct_answers(self):
        """Returns a queryset of correct answers for this question"""
        return self.answers.filter(is_correct=True)
    
    @property
    def incorrect_answers(self):
        """Returns a queryset of incorrect answers for this question"""
        return self.answers.filter(is_correct=False)
    
    @property
    def total_answers(self):
        """Returns the total number of answers for this question"""
        return self.answers.count()
    
    @property
    def correct_answers_count(self):
        """Returns the number of correct answers"""
        return self.correct_answers.count()
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        # Ensure domain belongs to the same exam
        if self.domain and self.exam and self.domain.exam != self.exam:
            raise ValidationError("Domain must belong to the same exam as the question.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Answer(models.Model):
    """Model representing answer options for questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(help_text="The answer option text")
    is_correct = models.BooleanField(default=False, help_text="Whether this answer is correct")
    explanation = models.TextField(
        blank=True,
        help_text="Explanation for why this answer is correct or incorrect (optional)"
    )
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text="Order of this answer option (1-7, typically 3-6 answers per question)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question', 'order']
        unique_together = ['question', 'order']
        indexes = [
            models.Index(fields=['question', 'order']),
            models.Index(fields=['is_correct']),
        ]
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
    
    def __str__(self):
        correct_indicator = "✓" if self.is_correct else "✗"
        return f"{correct_indicator} {self.answer_text[:30]}..."
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        # Ensure we don't have more than 7 answers per question
        if self.question:
            max_answers = 7
            existing_answers = Answer.objects.filter(question=self.question).exclude(pk=self.pk)
            if existing_answers.count() >= max_answers:
                raise ValidationError(f"A question cannot have more than {max_answers} answers.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# Signal to create default domains when an exam is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Exam)
def create_default_domains(sender, instance, created, **kwargs):
    """Create default domains when a new exam is created"""
    if created:
        # Default domains for Google Cloud Professional Developer
        if instance.name == Exam.GOOGLE_CLOUD_DEVELOPER:
            default_domains = [
                {
                    'name': 'Section 1: Designing highly scalable, available, and reliable cloud-native applications',
                    'order': 1,
                    'weight_percentage': 32.0
                },
                {
                    'name': 'Section 2: Building and testing applications',
                    'order': 2,
                    'weight_percentage': 20.0
                },
                {
                    'name': 'Section 3: Deploying applications',
                    'order': 3,
                    'weight_percentage': 16.0
                },
                {
                    'name': 'Section 4: Integrating Google Cloud services',
                    'order': 4,
                    'weight_percentage': 20.0
                },
                {
                    'name': 'Section 5: Managing application performance monitoring',
                    'order': 5,
                    'weight_percentage': 12.0
                },
            ]
            
            for domain_data in default_domains:
                Domain.objects.create(exam=instance, **domain_data)
        
        # Default domains for Google Cloud Professional Architect
        elif instance.name == Exam.GOOGLE_CLOUD_ARCHITECT:
            default_domains = [
                {
                    'name': 'Section 1: Designing and planning a cloud solution architecture',
                    'order': 1,
                    'weight_percentage': 24.0
                },
                {
                    'name': 'Section 2: Managing and provisioning solution infrastructure',
                    'order': 2,
                    'weight_percentage': 20.0
                },
                {
                    'name': 'Section 3: Designing for security and compliance',
                    'order': 3,
                    'weight_percentage': 20.0
                },
                {
                    'name': 'Section 4: Analyzing and optimizing technical and business processes',
                    'order': 4,
                    'weight_percentage': 18.0
                },
                {
                    'name': 'Section 5: Managing implementation',
                    'order': 5,
                    'weight_percentage': 10.0
                },
                {
                    'name': 'Section 6: Ensuring solution and operations reliability',
                    'order': 6,
                    'weight_percentage': 8.0
                },
            ]
            
            for domain_data in default_domains:
                Domain.objects.create(exam=instance, **domain_data)