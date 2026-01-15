from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Course, Lesson, CourseEnrollment


def course_list(request):
    courses = Course.objects.filter(is_published=True)

    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = list(
            CourseEnrollment.objects.filter(user=request.user).values_list('course_id', flat=True)
        )

    context = {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.filter(is_published=True).order_by('order', 'created_at')
    first_lesson = lessons.first()

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(
            user=request.user,
            course=course
        ).exists()

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'first_lesson': first_lesson,
    }
    return render(request, 'courses/course_detail.html', context)


def lesson_detail(request, course_slug, slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, course=course, slug=slug, is_published=True)
    course_lessons = course.lessons.filter(is_published=True).order_by('order', 'created_at')

    is_enrolled = False
    has_access = lesson.is_free
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(user=request.user, course=course).exists()
        if lesson.is_paid:
            has_access = is_enrolled

    previous_lesson = None
    next_lesson = None
    lesson_list = list(course_lessons)
    try:
        current_index = lesson_list.index(lesson)
        if current_index > 0:
            previous_lesson = lesson_list[current_index - 1]
        if current_index < len(lesson_list) - 1:
            next_lesson = lesson_list[current_index + 1]
    except ValueError:
        pass

    context = {
        'post': lesson,  # keep template variable name aligned with existing lesson template
        'course': course,
        'course_lessons': course_lessons,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'has_access': has_access,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/lesson_detail.html', context)


@login_required
@require_POST
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    CourseEnrollment.objects.get_or_create(user=request.user, course=course)
    return redirect(course.get_absolute_url())
