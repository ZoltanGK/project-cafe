from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Users
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 128)
    email = models.EmailField()
    
    def __str__(self):
        return self.user.username

class Staff(UserProfile):
    role = models.CharField(max_length = 128)

class Student(UserProfile):
    courses = models.CharField(256)
    lab_groups = models.CharField(256)

# Issues and Responses
class Issue(models.Model):
    id = models.IntegerField(max_length = 32)
    date = models.DateField()
    # Can also use TextField, but then length cannot be limited if I understand 
    # correctly
    content = models.CharField(1024)
    poster = models.ManyToManyField(UserProfile)
    anonymous = models.BooleanField()
    #TODO: Figure out what status corresponds to what
    status = models.IntegerField()

    def __str__(self):
        return self.id

class Response(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    number = models.IntegerField()
    date = models.DateField()
    content = models.CharField(1024)
    # If the User who posted the response is delete, keep the response
    poster = models.ForeignKey(UserProfile, on_delete=models.SET_NULL)

    def __str__(self):
        return self.issue.id + "." + self.number

# Categories
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    staff_resp = models.ManyToManyField(Staff)
    issues = models.ManyToManyField(Issue)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name