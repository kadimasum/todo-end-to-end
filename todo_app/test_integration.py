from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo, Category
from .test_factories import UserFactory, TodoFactory, CategoryFactory


class TodoAppIntegrationTest(TestCase):
    """Integration tests for the complete todo application workflow"""
    
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory()
    
    def test_complete_todo_workflow(self):
        """Test complete workflow from registration to todo management"""
        # 1. User registration
        registration_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(reverse('register'), data=registration_data)
        self.assertEqual(response.status_code, 302)  # Redirects after registration
        
        # 2. Login
        self.client.login(username='newuser', password='complexpassword123')
        
        # 3. Create category
        category_data = {
            'name': 'Work',
            'description': 'Work-related tasks',
            'color': '#007bff'
        }
        response = self.client.post(reverse('category_create'), data=category_data)
        self.assertEqual(response.status_code, 302)
        category = Category.objects.get(name='Work')
        
        # 4. Create todo
        todo_data = {
            'title': 'Complete project',
            'description': 'Finish the Django project',
            'priority': 'high',
            'category': category.id,
            'due_date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
        }
        response = self.client.post(reverse('todo_create'), data=todo_data)
        self.assertEqual(response.status_code, 302)
        todo = Todo.objects.get(title='Complete project')
        
        # 5. View todo list
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete project')
        
        # 6. View todo detail
        response = self.client.get(reverse('todo_detail', args=[todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete project')
        
        # 7. Edit todo
        edit_data = {
            'title': 'Complete project - Updated',
            'description': 'Finish the Django project with new requirements',
            'priority': 'urgent',
            'category': category.id,
            'due_date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
        }
        response = self.client.post(reverse('todo_edit', args=[todo.id]), data=edit_data)
        self.assertEqual(response.status_code, 302)
        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Complete project - Updated')
        self.assertEqual(todo.priority, 'urgent')
        
        # 8. Toggle todo completion
        response = self.client.post(reverse('todo_toggle', args=[todo.id]))
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertTrue(todo.completed)
        
        # 9. View dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # Total todos
        self.assertContains(response, '1')  # Completed todos
        
        # 10. Filter todos
        response = self.client.get(reverse('todo_list'), {'completed': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete project - Updated')
        
        # 11. Search todos
        response = self.client.get(reverse('todo_list'), {'search': 'project'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete project - Updated')
        
        # 12. Delete todo
        response = self.client.post(reverse('todo_delete', args=[todo.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(id=todo.id).exists())
    
    def test_multiple_users_isolation(self):
        """Test that users can only see their own todos"""
        # Create two users
        user1 = UserFactory()
        user2 = UserFactory()
        
        # Create todos for each user
        todo1 = TodoFactory(user=user1, title='User1 Todo')
        todo2 = TodoFactory(user=user2, title='User2 Todo')
        
        # User1 login and check they only see their todos
        self.client.login(username=user1.username, password='defaultpassword123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User1 Todo')
        self.assertNotContains(response, 'User2 Todo')
        
        # User2 login and check they only see their todos
        self.client.login(username=user2.username, password='defaultpassword123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User2 Todo')
        self.assertNotContains(response, 'User1 Todo')
    
    def test_todo_filtering_and_sorting(self):
        """Test comprehensive filtering and sorting functionality"""
        self.client.login(username=self.user.username, password='defaultpassword123')
        
        # Create test data
        category1 = CategoryFactory(name='Work', color='#007bff')
        category2 = CategoryFactory(name='Personal', color='#28a745')
        
        todo1 = TodoFactory(
            user=self.user,
            title='High Priority Work',
            priority='high',
            category=category1,
            completed=False
        )
        todo2 = TodoFactory(
            user=self.user,
            title='Low Priority Personal',
            priority='low',
            category=category2,
            completed=True
        )
        todo3 = TodoFactory(
            user=self.user,
            title='Medium Priority Work',
            priority='medium',
            category=category1,
            completed=False
        )
        
        # Test priority filter
        response = self.client.get(reverse('todo_list'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Priority Work')
        self.assertNotContains(response, 'Low Priority Personal')
        
        # Test category filter
        response = self.client.get(reverse('todo_list'), {'category': category1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Priority Work')
        self.assertContains(response, 'Medium Priority Work')
        self.assertNotContains(response, 'Low Priority Personal')
        
        # Test completed filter
        response = self.client.get(reverse('todo_list'), {'completed': 'true'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Low Priority Personal')
        self.assertNotContains(response, 'High Priority Work')
        
        # Test search
        response = self.client.get(reverse('todo_list'), {'search': 'Work'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'High Priority Work')
        self.assertContains(response, 'Medium Priority Work')
        self.assertNotContains(response, 'Low Priority Personal')
        
        # Test sorting by title
        response = self.client.get(reverse('todo_list'), {'sort_by': 'title'})
        self.assertEqual(response.status_code, 200)
        # Should be sorted alphabetically
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics accuracy"""
        self.client.login(username=self.user.username, password='defaultpassword123')
        
        # Create test todos
        TodoFactory(user=self.user, completed=True)
        TodoFactory(user=self.user, completed=True)
        TodoFactory(user=self.user, completed=False)
        TodoFactory(user=self.user, completed=False, due_date=timezone.now() - timedelta(days=1))
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check statistics
        self.assertContains(response, '4')  # Total todos
        self.assertContains(response, '2')  # Completed todos
        self.assertContains(response, '2')  # Pending todos
        self.assertContains(response, '1')  # Overdue todos
    
    def test_pagination(self):
        """Test pagination functionality"""
        self.client.login(username=self.user.username, password='defaultpassword123')
        
        # Create more than 10 todos (pagination limit)
        for i in range(15):
            TodoFactory(user=self.user, title=f'Todo {i}')
        
        # Test first page
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        # Check that we have todos on the first page
        self.assertTrue(response.context['page_obj'].has_other_pages())
        
        # Test second page
        response = self.client.get(reverse('todo_list'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        # Check that we have todos on the second page
        self.assertTrue(len(response.context['page_obj']) > 0)
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        self.client.login(username=self.user.username, password='defaultpassword123')
        
        # Test accessing non-existent todo
        response = self.client.get(reverse('todo_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)
        
        # Test invalid form submission
        response = self.client.post(reverse('todo_create'), data={'title': ''})
        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertContains(response, 'This field is required')
    
    def test_ajax_todo_toggle(self):
        """Test AJAX todo toggle functionality"""
        self.client.login(username=self.user.username, password='defaultpassword123')
        
        todo = TodoFactory(user=self.user, completed=False)
        
        # Test toggle via AJAX
        response = self.client.post(
            reverse('todo_toggle', args=[todo.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Check response is JSON
        import json
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['completed'])
        
        # Verify todo was actually toggled
        todo.refresh_from_db()
        self.assertTrue(todo.completed)
