from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Todo, Category
from .forms import TodoForm, CategoryForm, TodoFilterForm, CustomUserCreationForm


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('todo_list')
    return render(request, 'todo_app/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('todo_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def todo_list(request):
    """Main todo list view with filtering and pagination"""
    todos = Todo.objects.filter(user=request.user)
    
    # Apply filters
    filter_form = TodoFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        priority = filter_form.cleaned_data.get('priority')
        category = filter_form.cleaned_data.get('category')
        completed = filter_form.cleaned_data.get('completed')
        sort_by = filter_form.cleaned_data.get('sort_by') or '-created_at'
        
        if search:
            todos = todos.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        if priority:
            todos = todos.filter(priority=priority)
        
        if category:
            todos = todos.filter(category=category)
        
        if completed == 'true':
            todos = todos.filter(completed=True)
        elif completed == 'false':
            todos = todos.filter(completed=False)
        
        todos = todos.order_by(sort_by)
    else:
        todos = todos.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(todos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for the filter form
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'categories': categories,
        'total_todos': todos.count(),
        'completed_todos': todos.filter(completed=True).count(),
    }
    
    return render(request, 'todo_app/todo_list.html', context)


@login_required
def todo_detail(request, pk):
    """Detail view for a specific todo"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    return render(request, 'todo_app/todo_detail.html', {'todo': todo})


@login_required
def todo_create(request):
    """Create a new todo"""
    if request.method == 'POST':
        form = TodoForm(request.POST, user=request.user)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'Todo created successfully!')
            return redirect('todo_list')
    else:
        form = TodoForm(user=request.user)
    
    return render(request, 'todo_app/todo_form.html', {
        'form': form,
        'title': 'Create New Todo'
    })


@login_required
def todo_edit(request, pk):
    """Edit an existing todo"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Todo updated successfully!')
            return redirect('todo_detail', pk=todo.pk)
    else:
        form = TodoForm(instance=todo, user=request.user)
    
    return render(request, 'todo_app/todo_form.html', {
        'form': form,
        'title': 'Edit Todo',
        'todo': todo
    })


@login_required
@require_POST
def todo_toggle(request, pk):
    """Toggle todo completion status via AJAX"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    
    return JsonResponse({
        'success': True,
        'completed': todo.completed
    })


@login_required
def todo_delete(request, pk):
    """Delete a todo"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
        return redirect('todo_list')
    
    return render(request, 'todo_app/todo_confirm_delete.html', {'todo': todo})


@login_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    return render(request, 'todo_app/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'todo_app/category_form.html', {
        'form': form,
        'title': 'Create New Category'
    })


@login_required
def dashboard(request):
    """Dashboard with statistics and recent todos"""
    user_todos = Todo.objects.filter(user=request.user)
    
    # Statistics
    total_todos = user_todos.count()
    completed_todos = user_todos.filter(completed=True).count()
    pending_todos = total_todos - completed_todos
    overdue_todos = user_todos.filter(
        due_date__lt=timezone.now(),
        completed=False
    ).count()
    
    # Recent todos
    recent_todos = user_todos.order_by('-created_at')[:5]
    
    # Priority distribution
    priority_stats = {}
    for priority, _ in [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')]:
        priority_stats[priority] = user_todos.filter(priority=priority).count()
    
    context = {
        'total_todos': total_todos,
        'completed_todos': completed_todos,
        'pending_todos': pending_todos,
        'overdue_todos': overdue_todos,
        'recent_todos': recent_todos,
        'priority_stats': priority_stats,
    }
    
    return render(request, 'todo_app/dashboard.html', context)
