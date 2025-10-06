# TodoApp - Django Todo Management System

A modern, feature-rich todo management application built with Django, featuring an enticing user interface and comprehensive testing.

## 🚀 Features

### Core Functionality
- **User Authentication**: Registration, login, and user management
- **Todo Management**: Create, read, update, and delete todos
- **Category System**: Organize todos with custom categories and color coding
- **Priority Levels**: Low, Medium, High, and Urgent priority levels
- **Due Dates**: Set and track due dates with overdue detection
- **Status Tracking**: Mark todos as completed or pending

### Advanced Features
- **Smart Filtering**: Filter by priority, category, completion status, and search
- **Sorting Options**: Sort by date, title, priority, and more
- **Dashboard Analytics**: View statistics and progress tracking
- **Responsive Design**: Mobile-friendly interface
- **AJAX Interactions**: Smooth user experience with dynamic updates
- **Pagination**: Handle large numbers of todos efficiently

### User Interface
- **Modern Design**: Clean, professional interface with Bootstrap 5
- **Interactive Elements**: Smooth animations and transitions
- **Color Coding**: Visual priority and category indicators
- **Responsive Layout**: Works on all device sizes
- **Accessibility**: Keyboard navigation and screen reader support

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Testing**: pytest, pytest-django, factory-boy
- **Forms**: Django Crispy Forms with Bootstrap 5

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd django-server-devops
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## 🧪 Testing

The project includes comprehensive test coverage with unit tests, integration tests, and factory-based test data generation.

### Run All Tests
```bash
python manage.py test
```

### Run with pytest
```bash
pytest
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Model Tests**: Database model validation
- **View Tests**: HTTP request/response testing
- **Form Tests**: Form validation and processing
- **Permission Tests**: User access control testing

## 📁 Project Structure

```
django-server-devops/
├── manage.py
├── requirements.txt
├── pytest.ini
├── todo_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── todo_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── tests.py
│   ├── test_factories.py
│   └── test_integration.py
├── templates/
│   ├── base.html
│   ├── todo_app/
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── todo_list.html
│   │   ├── todo_detail.html
│   │   ├── todo_form.html
│   │   ├── todo_confirm_delete.html
│   │   ├── category_list.html
│   │   └── category_form.html
│   └── registration/
│       └── register.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🎯 Usage

### Getting Started
1. **Register**: Create a new account or login
2. **Dashboard**: View your todo statistics and recent activity
3. **Create Todos**: Add new tasks with descriptions, priorities, and due dates
4. **Organize**: Use categories to group related todos
5. **Track Progress**: Mark todos as complete and monitor your productivity

### Key Features Usage

#### Creating Todos
- Click "New Todo" to create a task
- Set title, description, priority, category, and due date
- Todos are automatically saved to your account

#### Filtering and Searching
- Use the filter panel to narrow down todos
- Search by title or description
- Filter by priority, category, or completion status
- Sort by various criteria

#### Categories
- Create custom categories with colors
- Assign todos to categories for better organization
- View todos by category

#### Dashboard
- Monitor your productivity with statistics
- View recent todos and priority distribution
- Quick access to common actions

## 🔧 Configuration

### Database Configuration
The project uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files
For production, configure static file serving:

```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Email Configuration
Configure email settings for user registration:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-host'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email'
EMAIL_HOST_PASSWORD = 'your-password'
```

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email settings
- [ ] Set up HTTPS
- [ ] Configure logging
- [ ] Set up monitoring

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "todo_project.wsgi:application"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Bug Reports

If you find a bug, please create an issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

## 💡 Feature Requests

Have an idea for a new feature? Please create an issue with:
- Detailed description
- Use case scenarios
- Potential implementation approach

## 📊 Performance

The application is optimized for performance with:
- Database indexing on frequently queried fields
- Pagination for large datasets
- Efficient query patterns
- Static file optimization
- Caching strategies (ready for implementation)

## 🔒 Security

Security features include:
- CSRF protection
- SQL injection prevention
- XSS protection
- User authentication and authorization
- Input validation and sanitization
- Secure password handling

## 📈 Future Enhancements

Potential future features:
- Real-time notifications
- File attachments
- Team collaboration
- Mobile app
- API endpoints
- Advanced analytics
- Calendar integration
- Email reminders

---

**Built with ❤️ using Django and modern web technologies**
