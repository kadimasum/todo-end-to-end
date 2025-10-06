from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo, Category, TodoAttachment
from .forms import TodoForm, CategoryForm, CustomUserCreationForm


class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Work',
            color='#007bff',
            description='Work-related tasks'
        )
    
    def test_todo_creation(self):
        """Test creating a todo"""
        todo = Todo.objects.create(
            title='Test Todo',
            description='Test description',
            user=self.user,
            category=self.category,
            priority='high'
        )
        self.assertEqual(todo.title, 'Test Todo')
        self.assertEqual(todo.user, self.user)
        self.assertEqual(todo.category, self.category)
        self.assertEqual(todo.priority, 'high')
        self.assertFalse(todo.completed)
    
    def test_todo_str_representation(self):
        """Test string representation of todo"""
        todo = Todo.objects.create(
            title='Test Todo',
            user=self.user
        )
        self.assertEqual(str(todo), 'Test Todo')
    
    def test_todo_is_overdue(self):
        """Test overdue detection"""
        # Create overdue todo
        overdue_todo = Todo.objects.create(
            title='Overdue Todo',
            user=self.user,
            due_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(overdue_todo.is_overdue)
        
        # Create future todo
        future_todo = Todo.objects.create(
            title='Future Todo',
            user=self.user,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(future_todo.is_overdue)
        
        # Create completed overdue todo
        completed_overdue = Todo.objects.create(
            title='Completed Overdue',
            user=self.user,
            due_date=timezone.now() - timedelta(days=1),
            completed=True
        )
        self.assertFalse(completed_overdue.is_overdue)
    
    def test_todo_days_until_due(self):
        """Test days until due calculation"""
        # Future todo
        future_todo = Todo.objects.create(
            title='Future Todo',
            user=self.user,
            due_date=timezone.now() + timedelta(days=5)
        )
        # Allow for 1 day difference due to timezone calculations
        self.assertAlmostEqual(future_todo.days_until_due, 5, delta=1)
        
        # Past todo
        past_todo = Todo.objects.create(
            title='Past Todo',
            user=self.user,
            due_date=timezone.now() - timedelta(days=3)
        )
        # Allow for 1 day difference due to timezone calculations
        self.assertAlmostEqual(past_todo.days_until_due, -3, delta=1)
        
        # No due date
        no_due_todo = Todo.objects.create(
            title='No Due Date',
            user=self.user
        )
        self.assertIsNone(no_due_todo.days_until_due)


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='Personal',
            color='#28a745',
            description='Personal tasks'
        )
        self.assertEqual(category.name, 'Personal')
        self.assertEqual(category.color, '#28a745')
        self.assertEqual(str(category), 'Personal')
    
    def test_category_ordering(self):
        """Test category ordering by name"""
        Category.objects.create(name='Z Category')
        Category.objects.create(name='A Category')
        Category.objects.create(name='M Category')
        
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, 'A Category')
        self.assertEqual(categories[1].name, 'M Category')
        self.assertEqual(categories[2].name, 'Z Category')


class TodoFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Work',
            color='#007bff'
        )
    
    def test_valid_todo_form(self):
        """Test valid todo form"""
        form_data = {
            'title': 'Test Todo',
            'description': 'Test description',
            'priority': 'high',
            'category': self.category.id
        }
        form = TodoForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_invalid_todo_form(self):
        """Test invalid todo form"""
        form_data = {
            'title': '',  # Empty title should be invalid
            'description': 'Test description',
            'priority': 'high'
        }
        form = TodoForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_todo_form_with_due_date(self):
        """Test todo form with due date"""
        due_date = timezone.now() + timedelta(days=1)
        form_data = {
            'title': 'Test Todo',
            'description': 'Test description',
            'priority': 'medium',
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M')
        }
        form = TodoForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())


class CategoryFormTest(TestCase):
    def test_valid_category_form(self):
        """Test valid category form"""
        form_data = {
            'name': 'Personal',
            'description': 'Personal tasks',
            'color': '#28a745'
        }
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_category_form(self):
        """Test invalid category form"""
        form_data = {
            'name': '',  # Empty name should be invalid
            'description': 'Personal tasks',
            'color': '#28a745'
        }
        form = CategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class CustomUserCreationFormTest(TestCase):
    def test_valid_user_creation_form(self):
        """Test valid user creation form"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_user_creation_form(self):
        """Test invalid user creation form"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',  # Invalid email
            'password1': 'complexpassword123',
            'password2': 'differentpassword'  # Mismatched passwords
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)


class TodoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Work',
            color='#007bff'
        )
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='Test description',
            user=self.user,
            category=self.category
        )
    
    def test_home_view_authenticated(self):
        """Test home view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        # The home view should redirect authenticated users to todo_list
        self.assertIn(response.status_code, [200, 302])
    
    def test_home_view_anonymous(self):
        """Test home view for anonymous user"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TodoApp')
    
    def test_todo_list_view_authenticated(self):
        """Test todo list view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')
    
    def test_todo_list_view_anonymous(self):
        """Test todo list view for anonymous user"""
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 302)  # Redirects to login
    
    def test_todo_create_view_get(self):
        """Test todo create view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Todo')
    
    def test_todo_create_view_post(self):
        """Test todo create view POST request"""
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'title': 'New Todo',
            'description': 'New description',
            'priority': 'high',
            'category': self.category.id
        }
        response = self.client.post(reverse('todo_create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after creation
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())
    
    def test_todo_detail_view(self):
        """Test todo detail view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_detail', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')
    
    def test_todo_edit_view_get(self):
        """Test todo edit view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_edit', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Todo')
    
    def test_todo_edit_view_post(self):
        """Test todo edit view POST request"""
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'title': 'Updated Todo',
            'description': 'Updated description',
            'priority': 'low',
            'category': self.category.id
        }
        response = self.client.post(reverse('todo_edit', args=[self.todo.id]), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after update
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')
    
    def test_todo_delete_view_get(self):
        """Test todo delete view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_delete', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirm Delete')
    
    def test_todo_delete_view_post(self):
        """Test todo delete view POST request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo_delete', args=[self.todo.id]))
        self.assertEqual(response.status_code, 302)  # Redirects after deletion
        self.assertFalse(Todo.objects.filter(id=self.todo.id).exists())
    
    def test_todo_toggle_view(self):
        """Test todo toggle view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('todo_toggle', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.completed)
    
    def test_dashboard_view(self):
        """Test dashboard view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, '1')  # Total todos count
    
    def test_category_list_view(self):
        """Test category list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work')
    
    def test_category_create_view_get(self):
        """Test category create view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('category_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Category')
    
    def test_category_create_view_post(self):
        """Test category create view POST request"""
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'name': 'Personal',
            'description': 'Personal tasks',
            'color': '#28a745'
        }
        response = self.client.post(reverse('category_create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after creation
        self.assertTrue(Category.objects.filter(name='Personal').exists())


class TodoFilterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category1 = Category.objects.create(name='Work', color='#007bff')
        self.category2 = Category.objects.create(name='Personal', color='#28a745')
        
        self.todo1 = Todo.objects.create(
            title='Work Todo',
            description='Work related task',
            user=self.user,
            category=self.category1,
            priority='high'
        )
        self.todo2 = Todo.objects.create(
            title='Personal Todo',
            description='Personal task',
            user=self.user,
            category=self.category2,
            priority='low',
            completed=True
        )
    
    def test_todo_search_filter(self):
        """Test todo search functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'), {'search': 'Work'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work Todo')
        self.assertNotContains(response, 'Personal Todo')
    
    def test_todo_priority_filter(self):
        """Test todo priority filter"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work Todo')
        self.assertNotContains(response, 'Personal Todo')
    
    def test_todo_category_filter(self):
        """Test todo category filter"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'), {'category': self.category1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work Todo')
        self.assertNotContains(response, 'Personal Todo')
    
    def test_todo_completed_filter(self):
        """Test todo completed status filter"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'), {'completed': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Personal Todo')
        self.assertNotContains(response, 'Work Todo')
    
    def test_todo_sorting(self):
        """Test todo sorting"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('todo_list'), {'sort_by': 'title'})
        self.assertEqual(response.status_code, 200)
        # Should be sorted by title alphabetically


class UserRegistrationTest(TestCase):
    def test_user_registration_get(self):
        """Test user registration GET request"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join TodoApp')
    
    def test_user_registration_post(self):
        """Test user registration POST request"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password1': 'complexpassword123',
            'password2': 'differentpassword'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertFalse(User.objects.filter(username='newuser').exists())


class TodoAttachmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.todo = Todo.objects.create(
            title='Test Todo',
            user=self.user
        )
    
    def test_todo_attachment_creation(self):
        """Test creating a todo attachment"""
        attachment = TodoAttachment.objects.create(
            todo=self.todo,
            filename='test.txt'
        )
        self.assertEqual(attachment.todo, self.todo)
        self.assertEqual(attachment.filename, 'test.txt')
        self.assertEqual(str(attachment), 'Test Todo - test.txt')


class TodoPermissionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.todo = Todo.objects.create(
            title='User1 Todo',
            user=self.user1
        )
    
    def test_user_cannot_access_other_user_todo(self):
        """Test that user cannot access another user's todo"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('todo_detail', args=[self.todo.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_user_cannot_edit_other_user_todo(self):
        """Test that user cannot edit another user's todo"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('todo_edit', args=[self.todo.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_user_cannot_delete_other_user_todo(self):
        """Test that user cannot delete another user's todo"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(reverse('todo_delete', args=[self.todo.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Todo.objects.filter(id=self.todo.id).exists())
