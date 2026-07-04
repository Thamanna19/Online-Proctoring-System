from django.db import models
from django.contrib.auth.models import User

# Student profile linked to Django User
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.course}"

# Exam model
class Exam(models.Model):
    title = models.CharField(max_length=200)
    course = models.CharField(max_length=10)
    duration_minutes = models.PositiveIntegerField()
    scheduled_date = models.DateTimeField()  # Still stored, only used for display

    def __str__(self):
        return f"{self.title} ({self.course})"
    
# Exam Questions
class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        default='A'
    )

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."

# Exam Result
class ExamResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}: {self.score}%"

# Suspicious activity log (for AI proctoring)
class SuspiciousActivity(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.reason} at {self.timestamp}"
