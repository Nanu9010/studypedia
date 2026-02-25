# ===== Management Commands =====
# Create: notes/management/commands/seed_universities.py
from django.core.management.base import BaseCommand
from university.models import University, Degree, Branch, Pattern, Semester, Subject


class Command(BaseCommand):
    help = 'Seed database with sample university data'

    def handle(self, *args, **options):
        # Sample data creation
        uni = University.objects.get_or_create(
            name="Mumbai University",
            defaults={'code': 'MU', 'location': 'Mumbai'}
        )[0]

        degree = Degree.objects.get_or_create(
            university=uni,
            name="Bachelor of Engineering",
            defaults={'duration_years': 4}
        )[0]

        cs_branch = Branch.objects.get_or_create(
            degree=degree,
            name="Computer Science",
            defaults={'code': 'CS'}
        )[0]

        # Create semesters
        for sem_num in range(1, 9):
            semester = Semester.objects.get_or_create(
                branch=cs_branch,
                number=sem_num
            )[0]

            # Add sample subjects for first semester
            if sem_num == 1:
                subjects = [
                    'Engineering Mathematics I',
                    'Engineering Physics',
                    'Engineering Chemistry',
                    'Programming in C',
                    'Engineering Graphics'
                ]
                for i, subject_name in enumerate(subjects, 1):
                    Subject.objects.get_or_create(
                        semester=semester,
                        name=subject_name,
                        defaults={'code': f'CS{sem_num}0{i}', 'credits': 3}
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded university data')
        )
