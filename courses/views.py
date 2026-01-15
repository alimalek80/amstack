from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Course, Lesson, CourseEnrollment


def course_list(request):
    courses = list(Course.objects.filter(is_published=True))

    enrollment_map = {}
    continue_links = {}
    if request.user.is_authenticated:
        enrollments = (
            CourseEnrollment.objects
            .filter(user=request.user, course__in=courses)
            .select_related('course', 'last_lesson')
        )
        for enrollment in enrollments:
            enrollment_map[enrollment.course_id] = enrollment
            lesson = enrollment.get_continue_lesson()
            if lesson:
                continue_links[enrollment.course_id] = lesson.get_absolute_url()
            else:
                continue_links[enrollment.course_id] = enrollment.course.get_absolute_url()

    course_cards = []
    for course in courses:
        is_enrolled = course.id in enrollment_map
        continue_url = continue_links.get(course.id, course.get_absolute_url())
        course_cards.append({
            'course': course,
            'is_enrolled': is_enrolled,
            'continue_url': continue_url,
        })

    context = {
        'course_cards': course_cards,
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

    # Persist resume progress for enrolled users
    if request.user.is_authenticated and is_enrolled:
        enrollment = CourseEnrollment.objects.filter(user=request.user, course=course).select_related('last_lesson').first()
        if enrollment:
            update_fields = []
            if enrollment.last_lesson_id != lesson.id:
                enrollment.last_lesson = lesson
                update_fields.append('last_lesson')

            total_lessons = len(lesson_list)
            if total_lessons:
                progress_pct = int(((current_index + 1) / total_lessons) * 100)
                if enrollment.progress != progress_pct:
                    enrollment.progress = progress_pct
                    update_fields.append('progress')

            if update_fields:
                enrollment.save(update_fields=update_fields)

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
