from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

# Users
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 128)
    email = models.EmailField()
    
    def __str__(self):
        return self.user.username

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length = 128)

    class Meta:
        verbose_name_plural = "staff"
    
    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.CharField(max_length = 256)
    lab_groups = models.CharField(max_length = 256)

    def __str__(self):
        return self.user.username

# Categories
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    staff_resp = models.ManyToManyField(Staff)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        # The below code should create a new responsibility permission for each category upon saving
        # These permissions will have to be manually assigned to Staff
        content_type = ContentType.objects.get_for_model(Category)
        Permission.objects.create(codename=f'resp-for-{self.slug}',
                                name=f'Responsible for {self.name}',
                                content_type=content_type,)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

# Issues and Responses
class Issue(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    categories = models.ManyToManyField(Category)
    # Can also use TextField, but then length cannot be limited if I understand 
    # correctly
    content = models.CharField(max_length = 1024)
    poster = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    anonymous = models.BooleanField()
    #TODO: Figure out what status corresponds to what
    status = models.IntegerField()

    def __str__(self):
        return str(self.id)

class Response(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    number = models.IntegerField()
    date = models.DateField()
    content = models.CharField(max_length = 1024)
    # If the User who posted the response is delete, keep the response
    poster = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.issue.id) + "." + str(self.number)
    
class Contact(models.Model):
    date = models.DateField()
    name = models.CharField(max_length = 64, default = 'Anonymous')
    issue = models.CharField(max_length = 1024)

    def __str__(self):
        return self.issue