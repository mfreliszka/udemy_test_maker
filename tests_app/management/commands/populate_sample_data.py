from django.core.management.base import BaseCommand
from django.db import transaction
from tests_app.models import Exam, Domain, Question, Answer


class Command(BaseCommand):
    help = 'Populate the database with sample exam questions for Google Cloud certifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exam',
            type=str,
            default='google_cloud_developer',
            help='Exam type to populate (google_cloud_developer, google_cloud_architect)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        exam_type = options['exam']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Question.objects.all().delete()
            Answer.objects.all().delete()
            Domain.objects.all().delete()
            Exam.objects.all().delete()

        with transaction.atomic():
            # Create Google Cloud Professional Developer exam
            if exam_type == 'google_cloud_developer':
                self.create_cloud_developer_data()
            elif exam_type == 'google_cloud_architect':
                self.create_cloud_architect_data()
            else:
                self.stdout.write(
                    self.style.ERROR(f'Unknown exam type: {exam_type}')
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated sample data for {exam_type}')
        )

    def create_cloud_developer_data(self):
        """Create sample data for Google Cloud Professional Developer exam"""
        
        # Create or get the exam
        exam, created = Exam.objects.get_or_create(
            name=Exam.GOOGLE_CLOUD_DEVELOPER,
            defaults={
                'display_name': 'Google Professional Cloud Developer',
                'description': 'A Professional Cloud Developer designs, builds, analyzes, and maintains cloud-native applications.',
                'provider': 'Google Cloud'
            }
        )
        
        if created:
            self.stdout.write(f'Created exam: {exam.display_name}')
        else:
            self.stdout.write(f'Using existing exam: {exam.display_name}')

        # Get the first domain (should be created by signal)
        domain = exam.domains.first()
        if not domain:
            domain = Domain.objects.create(
                exam=exam,
                name='Section 1: Designing highly scalable, available, and reliable cloud-native applications',
                order=1,
                weight_percentage=32.0
            )

        # Sample questions
        sample_questions = [
            {
                'test_number': 1,
                'question_text': 'You are developing a microservices application on Google Cloud. Your application needs to handle sudden traffic spikes while maintaining cost efficiency. Which Google Cloud service combination would best meet these requirements?',
                'question_type': Question.MULTIPLE_SELECT,
                'overall_explanation': 'Cloud Run with Cloud Load Balancing provides automatic scaling, serverless architecture, and cost efficiency for handling traffic spikes.',
                'answers': [
                    {'text': 'Cloud Run with Cloud Load Balancing', 'correct': True, 'explanation': 'Provides automatic scaling and serverless architecture'},
                    {'text': 'App Engine Standard with Cloud CDN', 'correct': True, 'explanation': 'Offers automatic scaling and global content distribution'},
                    {'text': 'Compute Engine with Managed Instance Groups', 'correct': False, 'explanation': 'Requires manual configuration and is not as cost-efficient for spiky traffic'},
                    {'text': 'Google Kubernetes Engine with Horizontal Pod Autoscaler', 'correct': True, 'explanation': 'Provides automatic scaling capabilities for containerized applications'},
                    {'text': 'Cloud Functions with Cloud Pub/Sub', 'correct': False, 'explanation': 'Better for event-driven architectures, not general web applications'},
                ]
            },
            {
                'test_number': 1,
                'question_text': 'Your application needs to store user session data that must be accessible across multiple regions with low latency. The data is frequently updated and needs strong consistency. Which storage solution should you choose?',
                'question_type': Question.MULTIPLE_CHOICE,
                'overall_explanation': 'Cloud Spanner provides global distribution, strong consistency, and low latency for frequently updated data.',
                'answers': [
                    {'text': 'Cloud Firestore in Native mode', 'correct': False, 'explanation': 'Good for document storage but not optimal for session data'},
                    {'text': 'Cloud Spanner', 'correct': True, 'explanation': 'Provides global distribution, strong consistency, and low latency'},
                    {'text': 'Cloud Bigtable', 'correct': False, 'explanation': 'Better for analytical workloads, not transactional data'},
                    {'text': 'Cloud Memorystore for Redis', 'correct': False, 'explanation': 'Regional service, not suitable for multi-region requirements'},
                ]
            },
            {
                'test_number': 2,
                'question_text': 'You need to implement a CI/CD pipeline for your containerized application. The pipeline should automatically build, test, and deploy to Google Kubernetes Engine when code is pushed to your Git repository. Which services should you use?',
                'question_type': Question.MULTIPLE_SELECT,
                'overall_explanation': 'Cloud Build provides automated CI/CD capabilities, while Cloud Source Repositories can trigger builds, and Artifact Registry stores container images.',
                'answers': [
                    {'text': 'Cloud Build for building and testing', 'correct': True, 'explanation': 'Provides automated build and test capabilities'},
                    {'text': 'Cloud Source Repositories for Git hosting', 'correct': True, 'explanation': 'Can trigger Cloud Build on code changes'},
                    {'text': 'Artifact Registry for storing container images', 'correct': True, 'explanation': 'Secure storage for Docker container images'},
                    {'text': 'Cloud Functions for deployment automation', 'correct': False, 'explanation': 'Not necessary when Cloud Build can handle deployment'},
                    {'text': 'Compute Engine for running build agents', 'correct': False, 'explanation': 'Cloud Build provides managed build infrastructure'},
                ]
            }
        ]

        # Create questions and answers
        for q_data in sample_questions:
            question = Question.objects.create(
                exam=exam,
                domain=domain,
                test_number=q_data['test_number'],
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                overall_explanation=q_data['overall_explanation'],
            )

            for i, answer_data in enumerate(q_data['answers'], 1):
                Answer.objects.create(
                    question=question,
                    answer_text=answer_data['text'],
                    is_correct=answer_data['correct'],
                    explanation=answer_data['explanation'],
                    order=i
                )

            self.stdout.write(f'Created question: {question.question_text[:50]}...')

    def create_cloud_architect_data(self):
        """Create sample data for Google Cloud Professional Architect exam"""
        
        # Create or get the exam
        exam, created = Exam.objects.get_or_create(
            name=Exam.GOOGLE_CLOUD_ARCHITECT,
            defaults={
                'display_name': 'Google Professional Cloud Architect',
                'description': 'A Professional Cloud Architect enables organizations to leverage Google Cloud technologies.',
                'provider': 'Google Cloud'
            }
        )

        if created:
            self.stdout.write(f'Created exam: {exam.display_name}')
        else:
            self.stdout.write(f'Using existing exam: {exam.display_name}')

        # Get the first domain
        domain = exam.domains.first()
        if not domain:
            domain = Domain.objects.create(
                exam=exam,
                name='Section 1: Designing and planning a cloud solution architecture',
                order=1,
                weight_percentage=24.0
            )

        # Sample architect questions
        sample_questions = [
            {
                'test_number': 1,
                'question_text': 'Your organization wants to migrate a legacy on-premises application to Google Cloud. The application has strict compliance requirements and needs to process sensitive data. Which migration strategy and security controls should you implement?',
                'question_type': Question.MULTIPLE_SELECT,
                'overall_explanation': 'For compliance and sensitive data, use a phased migration with VPC Service Controls, Customer-Managed Encryption Keys, and Private Google Access.',
                'answers': [
                    {'text': 'Implement VPC Service Controls for data perimeter security', 'correct': True, 'explanation': 'Provides additional security layer for sensitive resources'},
                    {'text': 'Use Customer-Managed Encryption Keys (CMEK)', 'correct': True, 'explanation': 'Gives you control over encryption keys for compliance'},
                    {'text': 'Enable Private Google Access for secure API access', 'correct': True, 'explanation': 'Allows secure access to Google services without public IPs'},
                    {'text': 'Use Google-managed encryption keys only', 'correct': False, 'explanation': 'May not meet strict compliance requirements for key management'},
                    {'text': 'Migrate everything at once using live migration', 'correct': False, 'explanation': 'Risky approach for applications with strict compliance requirements'},
                ]
            }
        ]

        # Create questions and answers
        for q_data in sample_questions:
            question = Question.objects.create(
                exam=exam,
                domain=domain,
                test_number=q_data['test_number'],
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                overall_explanation=q_data['overall_explanation'],
            )

            for i, answer_data in enumerate(q_data['answers'], 1):
                Answer.objects.create(
                    question=question,
                    answer_text=answer_data['text'],
                    is_correct=answer_data['correct'],
                    explanation=answer_data['explanation'],
                    order=i
                )

            self.stdout.write(f'Created question: {question.question_text[:50]}...')