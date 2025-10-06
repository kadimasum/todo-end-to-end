from django.contrib import admin
from .models import Category, Todo, TodoAttachment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'category', 'completed', 'due_date', 'created_at']
    list_filter = ['completed', 'priority', 'category', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['completed', 'priority']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Organization', {
            'fields': ('category', 'priority')
        }),
        ('Status', {
            'fields': ('completed', 'due_date')
        }),
    )


@admin.register(TodoAttachment)
class TodoAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'todo', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'todo__title']
    ordering = ['-uploaded_at']
