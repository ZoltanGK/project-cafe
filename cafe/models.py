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

    def is_student(self):
        isStudent = False
        if self.user("staff")==True:
            isStudent = True
        return isStudent

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length = 128)

    class Meta:
        verbose_name_plural = "staff"
    
    def __str__(self):
        return self.user.username

    def get_cats_resp(self):
        # Returns all the categories given staff member is responsible for
        cats = []
        for c in Category.objects.all():
            if self.user.has_perm(f"cafe.resp-for-{c.slug}"):
                cats.append(c)
        return cats

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

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        # The below code should create a new responsibility permission for each category upon saving
        # These permissions will have to be manually assigned to Staff
        content_type = ContentType.objects.get_for_model(Category)
        Permission.objects.create(codename=f'resp-for-{self.slug}',
                                name=f'Responsible for {self.name}',
                                content_type=content_type,)
        super(Category, self).save(*args, **kwargs)
    
    @property
    def issues(self):
        return Issue.objects.filter(categories__id = self.id)

# Issues and Responses
class Issue(models.Model):
    date = models.DateField(auto_now_add=True)
    categories = models.ManyToManyField(Category)
    title = models.CharField(max_length = 64)
    # Can also use TextField, but we opted to have a limited length
    content = models.CharField(max_length = 1024)
    poster = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    anonymous = models.BooleanField(default=False)
    # Not currently fully utilised
    status = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    def in_categories(self):
        category_names = []
        for cat in self.categories.all():
            category_names.append(cat.name)
        return ", ".join(category_names)

    @property
    def responses(self):
        return [i for i in Response.objects.filter(issue = self)]

class Response(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    # This is technically the id of a response
    number = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    content = models.CharField(max_length = 1024)
    # Even if the User who posted the response is deleted, keep the response
    poster = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    anonymous = models.BooleanField(default=False)

    def __str__(self):
        return str(self.issue.id) + "." + str(self.number)
    
class Contact(models.Model):
    date = models.DateField(auto_now_add=True)
    name = models.CharField(max_length = 64, default = 'Anonymous')
    issue = models.CharField(max_length = 1024)

    def __str__(self):
        return self.issue