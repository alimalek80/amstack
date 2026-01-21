# 🚨 Production 500 Error Troubleshooting Guide

## Quick Steps to Debug Your cPanel 500 Error

### Step 1: Enable Detailed Error Logging (IMMEDIATE ACTION)

1. **Upload the debugging files** from this project to your cPanel file manager:
   - `debug_production.py`
   - `production_settings.py` 

2. **Create logs directory** in your project root:
   ```bash
   mkdir logs
   chmod 755 logs
   ```

3. **Temporarily enable DEBUG mode** (ONLY for debugging):
   - In cPanel, find your environment variables or `.env` file
   - Set: `DJANGO_DEBUG=True`
   - **IMPORTANT: Set back to False after debugging!**

### Step 2: Run Diagnostic Script

1. **SSH into your cPanel** or use the terminal:
   ```bash
   cd /path/to/your/django/project
   python debug_production.py
   ```

2. **Check the output** - it will show you:
   - Database connectivity issues
   - Missing packages
   - File permission problems
   - Environment variable issues

### Step 3: Check Log Files

After running the diagnostic, check these files for error details:
- `logs/django_errors.log`
- `logs/blog_errors.log`
- `logs/django_debug.log`

### Step 4: Common 500 Error Causes & Solutions

#### 🔍 **Missing Dependencies**
```bash
# Install missing packages
pip install markdown bleach pygments Pillow
```

#### 🔍 **Database Issues**
- Verify database credentials in environment variables
- Check if database exists and is accessible
- Run migrations: `python manage.py migrate`

#### 🔍 **File Permissions**
```bash
# Fix permissions
chmod 755 /path/to/your/project
chmod 755 /path/to/your/project/media
chmod 755 /path/to/your/project/static
chmod -R 644 /path/to/your/project/media/*
```

#### 🔍 **Static/Media Files**
```bash
# Collect static files
python manage.py collectstatic --noinput
```

#### 🔍 **Environment Variables Missing**
Add these to your cPanel environment:
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
```

### Step 5: Blog-Specific Issues

#### 🔍 **Image Upload Problems**
- Check if `media/blog/` directory exists and is writable
- Verify Pillow is installed: `pip show Pillow`

#### 🔍 **Markdown Processing Issues**
- Install required packages: `pip install markdown bleach pygments`
- Check if content has special characters causing encoding issues

#### 🔍 **User Profile Issues**
- Verify all users have profiles (signals should create them automatically)
- Check: `python manage.py shell` then `from accounts.models import User; User.objects.filter(profile__isnull=True)`

### Step 6: cPanel-Specific Checks

1. **Check cPanel Error Logs**:
   - Go to cPanel → Error Logs
   - Look for Python/Django errors around the time you got 500 error

2. **Python Version**:
   - Ensure you're using the correct Python version in cPanel
   - Check if virtual environment is activated

3. **File Structure**:
   ```
   /home/username/
   ├── public_html/
   │   ├── static/     # Static files here
   │   ├── media/      # Media files here
   │   └── .htaccess
   ├── your-django-project/
   │   ├── manage.py
   │   ├── requirements.txt
   │   └── logs/       # Create this directory
   ```

4. **Passenger WSGI File** (if using Passenger):
   ```python
   import sys
   import os
   
   # Add project directory to path
   sys.path.insert(0, os.path.dirname(__file__))
   
   # Set Django settings module
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

### Step 7: Testing the Fix

1. **Test blog post creation** in admin panel first
2. **Check logs** for any new errors
3. **Try creating posts** with different content types
4. **Test image uploads** if using them

### Emergency Commands

If you need to quickly check what's happening:

```bash
# Check database connectivity
python manage.py dbshell

# Check if migrations are needed
python manage.py showmigrations

# Create superuser if needed
python manage.py createsuperuser

# Test imports
python -c "import django; print(django.VERSION)"
python -c "import markdown, bleach, pygments; print('All packages OK')"
```

### When to Contact Support

Contact your hosting provider if:
- Database connection keeps failing despite correct credentials
- File permissions keep resetting
- Python packages won't install
- Server returns 500 errors for all Django applications

---

## 📞 Quick Debug Checklist

- [ ] Logs directory created and writable
- [ ] DEBUG=True set temporarily
- [ ] Ran debug_production.py script
- [ ] Checked django_errors.log file
- [ ] Verified all environment variables
- [ ] Confirmed database connectivity
- [ ] Installed all required packages
- [ ] Ran collectstatic
- [ ] Checked file permissions
- [ ] Tested in Django admin first
- [ ] Set DEBUG=False after debugging

Remember: Always set DEBUG=False in production after debugging!