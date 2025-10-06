import factory
from django.contrib.auth.models import User
from .models import Todo, Category, TodoAttachment


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or 'defaultpassword123'
        self.set_password(password)
        if create:
            self.save()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category {n}')
    color = factory.Faker('hex_color')
    description = factory.Faker('sentence')


class TodoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Todo
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    priority = factory.Iterator(['low', 'medium', 'high', 'urgent'])
    completed = factory.Faker('boolean')
    due_date = factory.Faker('future_datetime', end_date='+30d')


class TodoAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TodoAttachment
    
    todo = factory.SubFactory(TodoFactory)
    filename = factory.Faker('file_name', extension='txt')
