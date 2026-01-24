# API Documentation

## Overview
This API provides endpoints for accessing blog posts with proper access control:
- **Free posts**: Accessible to everyone without authentication
- **Paid posts**: List and metadata accessible to everyone, but full content requires purchase

## Base URL

**Development:**
```
http://localhost:8000/api/v1/
```

**Production:**
```
https://amstack.org/api/v1/
```

> Replace `{BASE_URL}` in examples below with your environment's base URL

## Authentication
The API uses JWT (JSON Web Tokens) for authentication.

### Register User
```http
POST {BASE_URL}/auth/register/
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "full_name": "Test User"
}
```

### Login
```http
POST {BASE_URL}/auth/login/
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "securepassword123"
}
```

Response:
```json
{
    "user": {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "date_joined": "2026-01-24T10:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### Using JWT Token
Include in headers:
```
Authorization: Bearer <access_token>
```

## Blog Endpoints

### 1. Free Posts (Accessible to Everyone)

#### List Free Posts
```http
GET {BASE_URL}/posts/free/
```

#### Get Free Post Detail
```http
GET {BASE_URL}/posts/free/{slug}/
```

### 2. Paid Posts (Content Access Controlled)

#### List Paid Posts
```http
GET {BASE_URL}/posts/paid/
```
*Note: Returns post metadata but content is restricted*

#### Get Paid Post Detail
```http
GET {BASE_URL}/posts/paid/{slug}/
```
*Note: Content depends on user's purchase status*

### 3. All Posts (Mixed)

#### List All Posts
```http
GET {BASE_URL}/posts/
```

#### Get Post Detail
```http
GET {BASE_URL}/posts/{slug}/
```

### 4. Categories

#### List Categories
```http
GET {BASE_URL}/categories/
```

#### List Posts in Category
```http
GET {BASE_URL}/categories/{slug}/posts/
```

### 5. Tags

#### List Tags
```http
GET {BASE_URL}/tags/
```

#### List Posts with Tag
```http
GET {BASE_URL}/tags/{slug}/posts/
```

### 6. Search and Special Endpoints

#### Search Posts
```http
GET {BASE_URL}/posts/search/?q=django&type=free
```
Parameters:
- `q`: Search query
- `type`: 'free', 'paid', or empty for all

#### Featured Posts
```http
GET {BASE_URL}/posts/featured/
```

#### Latest Posts
```http
GET {BASE_URL}/posts/latest/?limit=5
```

### 7. User-Specific Endpoints (Require Authentication)

#### Check Access to Paid Post
```http
POST {BASE_URL}/user/check-access/
Authorization: Bearer <token>
Content-Type: application/json

{
    "post_id": 123
}
```

Response:
```json
{
    "post_id": 123,
    "has_access": false,
    "purchase_required": true,
    "price": "29.99",
    "title": "Advanced Django Tutorial",
    "slug": "advanced-django-tutorial"
}
```

#### User's Purchased Posts
```http
GET {BASE_URL}/user/purchased-posts/
Authorization: Bearer <token>
```

## Response Examples

### Post List Response
```json
{
    "count": 50,
    "next": "{BASE_URL}/posts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Getting Started with Django",
            "slug": "getting-started-django",
            "excerpt": "Learn the basics of Django web framework...",
            "cover_image": "/media/blog/django-cover.jpg",
            "published_at": "2026-01-20T10:00:00Z",
            "reading_time": 5,
            "is_featured": true,
            "is_free": true,
            "price": "0.00",
            "post_type": "tutorial",
            "category": {
                "id": 1,
                "name": "Web Development",
                "slug": "web-development"
            },
            "tags": [
                {
                    "id": 1,
                    "name": "Django",
                    "slug": "django",
                    "color": "blue"
                }
            ],
            "author": {
                "id": 1,
                "email": "admin@example.com",
                "full_name": "Admin User"
            },
            "is_accessible": true
        }
    ]
}
```

### Post Detail Response (Free Post)
```json
{
    "id": 1,
    "title": "Getting Started with Django",
    "slug": "getting-started-django",
    "excerpt": "Learn the basics of Django web framework...",
    "content": "# Getting Started with Django\n\nDjango is a high-level Python web framework...",
    "cover_image": "/media/blog/django-cover.jpg",
    "published_at": "2026-01-20T10:00:00Z",
    "updated_at": "2026-01-20T10:00:00Z",
    "reading_time": 5,
    "is_featured": true,
    "is_free": true,
    "price": "0.00",
    "post_type": "tutorial",
    "category": {
        "id": 1,
        "name": "Web Development",
        "slug": "web-development"
    },
    "tags": [
        {
            "id": 1,
            "name": "Django",
            "slug": "django",
            "color": "blue"
        }
    ],
    "author": {
        "id": 1,
        "email": "admin@example.com",
        "full_name": "Admin User"
    },
    "get_seo_title": "Getting Started with Django - Complete Guide",
    "get_meta_description": "Learn the basics of Django web framework...",
    "get_keywords_list": ["django", "python", "web development"],
    "is_accessible": true
}
```

### Post Detail Response (Paid Post - No Access)
```json
{
    "id": 2,
    "title": "Advanced Django Patterns",
    "slug": "advanced-django-patterns",
    "excerpt": "Master advanced Django development patterns...",
    "content": "# Advanced Django Patterns\n\nThis tutorial covers advanced concepts... [Content locked - Purchase required]",
    "cover_image": "/media/blog/advanced-django.jpg",
    "published_at": "2026-01-22T10:00:00Z",
    "updated_at": "2026-01-22T10:00:00Z",
    "reading_time": 15,
    "is_featured": false,
    "is_free": false,
    "price": "29.99",
    "post_type": "tutorial",
    "is_accessible": false
}
```

## Query Parameters

### Filtering
- `category`: Filter by category ID
- `post_type`: Filter by post type ('tutorial', 'article')
- `is_featured`: Filter featured posts (true/false)
- `is_free`: Filter by free/paid status (true/false)

### Search
- `search`: Search in title, excerpt, content

### Ordering
- `ordering`: Order by fields ('-published_at', 'title', 'price', etc.)

### Pagination
- `page`: Page number
- `page_size`: Items per page (max 100)

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "field_name": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "error": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "error": "Not found."
}
```

## Rate Limiting
- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour

## Example Usage with curl

### Get Free Posts
```bash
# Development
curl -X GET "http://localhost:8000/api/v1/posts/free/" \
  -H "Accept: application/json"

# Production
curl -X GET "https://amstack.org/api/v1/posts/free/" \
  -H "Accept: application/json"
```

### Login and Get Token
```bash
# Development
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'

# Production
curl -X POST "https://amstack.org/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Access Protected Endpoint
```bash
# Development
curl -X GET "http://localhost:8000/api/v1/user/purchased-posts/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Accept: application/json"

# Production
curl -X GET "https://amstack.org/api/v1/user/purchased-posts/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Accept: application/json"
```

### Check Paid Post Access
```bash
# Development
curl -X POST "http://localhost:8000/api/v1/user/check-access/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 123
  }'

# Production
curl -X POST "https://amstack.org/api/v1/user/check-access/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 123
  }'
```