
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import StudentRegisterForm, StudentProfileForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Exam, ExamQuestion, ExamResult, StudentProfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import SuspiciousActivity
import json
from django.http import HttpResponse
import base64
import cv2
import numpy as np



def homepage(request):
    return render(request, 'home.html')

def student_register(request):
    if request.method == 'POST':
        user_form = StudentRegisterForm(request.POST)
        profile_form = StudentProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)  # Hash the password
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('login')  # Redirect to login page
    else:
        user_form = StudentRegisterForm()
        profile_form = StudentProfileForm()
    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def student_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Go to student dashboard
        else:
            error = "Invalid username or password"
    return render(request, 'login.html', {'error': error})

@login_required
def student_dashboard(request):
    profile = request.user.studentprofile
    courses = ['MPC', 'BIPC', 'MEC', 'IEC', 'HPGE']
    return render(request, 'student_dashboard.html', {
        'course': profile.course,
        'courses': courses
    })

from .models import Exam, ExamResult, StudentProfile

@login_required
def student_course_view(request, course_code):
    user = request.user
    student = user.studentprofile

    # Get all exams for this course
    exams = Exam.objects.filter(course=course_code).order_by('scheduled_date')

    # Find exams the student has completed
    completed_exam_ids = ExamResult.objects.filter(
        student=student
    ).values_list('exam_id', flat=True)

    # Separate upcoming and completed exams (based only on whether the student has taken them)
    completed_exams = exams.filter(id__in=completed_exam_ids)
    upcoming_exams = exams.exclude(id__in=completed_exam_ids)

    return render(request, 'student_course_view.html', {
        'course': course_code,
        'upcoming_exams': upcoming_exams,
        'completed_exams': completed_exams
    })

@staff_member_required
def admin_dashboard(request):
    courses = ['MPC', 'BIPC', 'MEC', 'IEC', 'HPGE']
    return render(request, 'admin_dashboard.html', {'courses': courses})

@staff_member_required
def admin_course_view(request, course_code):
    students = StudentProfile.objects.filter(course=course_code)
    return render(request, 'admin_course.html', {
        'course': course_code,
        'students': students
    })

@staff_member_required
def create_question_paper(request, exam_id):
    # Add logic to create questions for a specific exam
    pass

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student_profile = request.user.studentprofile

    # Check if already submitted
    if ExamResult.objects.filter(student=student_profile, exam=exam).exists():
        return render(request, 'already_submitted.html', {
            'exam': exam,
            'course_code': exam.course
        })

    questions = ExamQuestion.objects.filter(exam=exam)

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected and selected == question.correct_option:
                score += 1

        percentage = (score / total) * 100 if total > 0 else 0

        # Save result
        ExamResult.objects.create(
            student=student_profile,
            exam=exam,
            score=percentage
        )

        # ✅ Show exam submitted message
        return render(request, 'exam_submitted.html', {
            'exam': exam,
            'course_code': exam.course
        })

    return render(request, 'take_exam.html', {
        'exam': exam,
        'questions': questions,
        'course_code': exam.course
    })
    
@staff_member_required
def create_question(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    if request.method == 'POST':
        qtype = request.POST['question_type']
        text = request.POST['question_text']
        options = request.POST.get('options')
        correct = request.POST['correct_answer']
        Question.objects.create(
            exam=exam,
            question_text=text,
            question_type=qtype,
            options=options,
            correct_answer=correct
        )
        return redirect('admin_course_view', course_code=exam.course)
    return render(request, 'create_question.html', {'exam': exam})

def custom_admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")
            return redirect('custom_admin_login')

    return render(request, 'admin_login.html')

@staff_member_required
def create_exam(request, course_code):
    if request.method == "POST":
        title = request.POST['title']
        duration = int(request.POST['duration'])
        scheduled_date = request.POST['scheduled_date']

        # Create exam
        exam = Exam.objects.create(
            title=title,
            course=course_code,
            duration_minutes=duration,
            scheduled_date=scheduled_date
        )

        # Process questions
        questions = zip(
            request.POST.getlist('question'),
            request.POST.getlist('a'),
            request.POST.getlist('b'),
            request.POST.getlist('c'),
            request.POST.getlist('d'),
            request.POST.getlist('correct')
        )

        for q_text, a, b, c, d, correct in questions:
            if q_text.strip() and correct.strip():
                ExamQuestion.objects.create(
                    exam=exam,
                    question_text=q_text,
                    option_a=a,
                    option_b=b,
                    option_c=c,
                    option_d=d,
                    correct_option=correct.upper()
                )

        return redirect('admin_course_view', course_code=course_code)

    return render(request, 'create_exam.html', {'course_code': course_code})

@login_required
def confirm_exam_start(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        # Redirect to start the actual exam
        return redirect('take_exam', exam_id=exam.id)

    return render(request, 'confirm_exam_start.html', {
        'exam': exam
    })

@csrf_exempt
@login_required
def face_check(request):
    import base64
    import cv2
    import numpy as np
    import json

    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image'].split(',')[1]
        exam_id = data['exam_id']
        
        # Decode the image
        image_bytes = base64.b64decode(image_data)
        np_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Convert to grayscale and detect faces
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        # Set status for JS to handle
        if len(faces) == 0:
            SuspiciousActivity.objects.create(
                student=request.user.studentprofile,
                exam_id=exam_id,
                reason="Face not detected"
            )
            return JsonResponse({'status': 'no_face'})

        elif len(faces) > 1:
            SuspiciousActivity.objects.create(
                student=request.user.studentprofile,
                exam_id=exam_id,
                reason="Multiple faces detected"
            )
            return JsonResponse({'status': 'multiple_faces'})

        return JsonResponse({'status': 'ok'})

@csrf_exempt
@login_required
def log_suspicious(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reason = data.get('reason')
        exam_id = data.get('exam_id')

        SuspiciousActivity.objects.create(
            student=request.user.studentprofile,
            exam_id=exam_id,
            reason=reason
        )
        return JsonResponse({'status': 'logged'})

    return JsonResponse({'status': 'error'}, status=400)