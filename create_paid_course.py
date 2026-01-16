#!/usr/bin/env python
"""
Create a sample paid course for testing e-commerce functionality
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from courses.models import Course, Lesson
from django.utils import timezone
from django.utils.text import slugify

def create_paid_course():
    print("🎓 Creating Sample Paid Course...")
    
    # Create the course
    course_title = "Full-Stack React & Django Masterclass"
    course_slug = slugify(course_title)
    
    course, created = Course.objects.get_or_create(
        slug=course_slug,
        defaults={
            'title': course_title,
            'description': """Master modern web development with this comprehensive course covering React frontend and Django backend development. 

Build real-world applications from scratch using industry best practices.

**What you'll learn:**
- React fundamentals and advanced patterns
- Django REST API development
- Authentication & Authorization
- Database design and optimization
- Deployment strategies
- Testing methodologies

**Prerequisites:** Basic knowledge of Python and JavaScript

**Duration:** 8 hours of content across 12 lessons""",
            'is_published': True,
            'is_free': False,
            'price': 89.99,
        }
    )
    
    if created:
        print(f"✅ Created course: {course.title} - ${course.price}")
    else:
        print(f"📝 Course already exists: {course.title} - ${course.price}")
    
    # Create lessons
    lessons_data = [
        {
            'title': '1. Course Introduction & Setup',
            'excerpt': 'Welcome to Full-Stack Development! Learn what you\'ll build and set up your development environment.',
            'content': """# Welcome to Full-Stack Development!

In this introductory lesson, we'll cover:

## What You'll Build
- A complete e-commerce application
- React frontend with modern hooks
- Django REST API backend
- User authentication system
- Payment processing integration

## Development Environment
- Node.js and npm/yarn setup
- Python and Django installation
- Code editor configuration
- Git workflow best practices

## Course Structure
This course is divided into 3 main sections:
1. **Frontend Development** (Lessons 2-5)
2. **Backend Development** (Lessons 6-9)
3. **Integration & Deployment** (Lessons 10-12)

Let's get started! 🚀""",
            'order': 1,
        },
        {
            'title': '2. React Fundamentals Review',
            'excerpt': 'Review React basics including components, JSX, state management, and the useEffect hook.',
            'content': """# React Fundamentals

Before we dive into advanced concepts, let's review React basics.

## Components & JSX
```jsx
function Welcome({ name }) {
    return <h1>Hello, {name}!</h1>;
}
```

## State Management with useState
```jsx
import { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <button onClick={() => setCount(count + 1)}>
            Count: {count}
        </button>
    );
}
```

## Effect Hook
```jsx
import { useEffect, useState } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        fetchUser(userId).then(setUser);
    }, [userId]);
    
    return user ? <div>{user.name}</div> : <div>Loading...</div>;
}
```

## Practice Exercise
Create a simple todo app using these concepts.""",
            'order': 2,
        },
        {
            'title': '3. Advanced React Patterns',
            'excerpt': 'Master advanced React patterns including custom hooks, Context API, and performance optimization.',
            'content': """# Advanced React Patterns

## Custom Hooks
```jsx
function useAuth() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        // Authentication logic
        checkAuthStatus().then(user => {
            setUser(user);
            setLoading(false);
        });
    }, []);
    
    return { user, loading };
}
```

## Context API for State Management
```jsx
const AuthContext = createContext();

export function AuthProvider({ children }) {
    const auth = useAuth();
    return (
        <AuthContext.Provider value={auth}>
            {children}
        </AuthContext.Provider>
    );
}
```

## Performance Optimization
- React.memo for component memoization
- useMemo and useCallback hooks
- Code splitting with React.lazy

## Assignment
Implement a shopping cart using Context API.""",
            'order': 3,
        },
        {
            'title': '4. Django REST API Basics',
            'excerpt': 'Learn to build REST APIs with Django REST Framework, including serializers and viewsets.',
            'content': """# Building REST APIs with Django

## Setting Up Django REST Framework
```bash
pip install djangorestframework
pip install django-cors-headers
```

## Creating Serializers
```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image']
```

## API Views
```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

## URL Configuration
```python
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
urlpatterns = router.urls
```

## Testing Your API
Use tools like Postman or Django REST Framework's browsable API.""",
            'order': 4,
        },
        {
            'title': '5. Authentication & JWT',
            'excerpt': 'Implement user authentication with JWT tokens for secure API access.',
            'content': """# User Authentication with JWT

## JWT Token Authentication
```python
# settings.py
INSTALLED_APPS = [
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

## Login/Register Views
```python
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
]
```

## Frontend Integration
```javascript
const login = async (credentials) => {
    const response = await fetch('/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
    });
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data;
};
```

## Protected Routes
Implement route guards in your React app.""",
            'order': 5,
        },
        {
            'title': '6. Database Design & Models',
            'excerpt': 'Advanced database design for e-commerce applications with Django models.',
            'content': """# Advanced Database Design

## E-commerce Models
```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

## Database Optimization
- Indexing strategies
- Query optimization with select_related and prefetch_related
- Database migrations best practices""",
            'order': 6,
        },
    ]
    
    # Create lessons
    for lesson_data in lessons_data:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=lesson_data['title'],
            defaults={
                'excerpt': lesson_data['excerpt'],
                'content': lesson_data['content'],
                'order': lesson_data['order'],
                'is_published': True,
                'is_free': False,  # Paid course lessons
            }
        )
        
        if created:
            print(f"  ✅ Created lesson: {lesson.title}")
        else:
            print(f"  📝 Lesson exists: {lesson.title}")
    
    print(f"\n🎉 Course ready!")
    print(f"📚 Title: {course.title}")
    print(f"💰 Price: ${course.price}")
    print(f"📖 Lessons: {course.lessons.count()}")
    print(f"🔗 URL: /courses/{course.slug}/")
    print("\nUsers can now purchase this course through the e-commerce system!")

if __name__ == '__main__':
    create_paid_course()