from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField,EmailField, IntegerField, NullBooleanField
import re
import bcrypt

# Create your models here.

class UserManager(models.Manager):
    def login_validator(self, postData):
        errors = {}
        if len(postData['email_login'])==0:
            errors['blank_email'] = "Login email cannot be blank!"
        existing_user = User.objects.filter(email=postData['email_login'])
        if not existing_user:
            errors['unregistered email'] = "Invalid Credentials"
        else:
            logged_user = existing_user[0]
            if len(postData['pw_login'])==0:
                errors['pasword'] = "Login password cannot be blank!"
            if bcrypt.checkpw(postData['pw_login'].encode(), existing_user[0].hashpass.encode()) != True:
                errors['credentials'] = "Invalid credentials!"
        return errors
    def reg_validator(self, postData):
        errors = {}
        if len(postData['first_name'])<2:
            errors['first_name'] = "First name must be at least 2 characters!"
        if len(postData['last_name'])<2:   
            errors['last_name'] = "Last name must be at least 2 characters!"
        if len(postData['password'])<8:   
            errors['password'] = "Password must be at least 8 characters!"
        if (postData['conf_pw']) != (postData['password']):
            errors['conf_pw'] = "passwords do not match!"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if len(postData['email'])==0:
            errors['email'] = 'Email cannot be blank'
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = ("Invalid email address!")
        current_users = User.objects.filter(email=postData['email'])
        if len(current_users)>0:
            errors['duplicate'] = 'Try again, email is already in use'
        return errors
    def comic_validator(self, postData):
        errors = {}
        if len(postData['upc'])<17:
            errors['upc'] = "Please enter full 17 digit upc code"
        # uploaded_comics = Comic.objects.filter(upc=postData['upc'])
        # if len(uploaded_comics)>0:
        #     errors['duplicate'] = 'That comic is already in library'
        return errors
    def collection_validator(self, postData):
        errors = {}
        if len(postData['new_col_name'])<1:
            errors['col_name'] = "Don't forget to name your collection"
        return errors

class User(models.Model):
    first_name=models.CharField(max_length=15)
    last_name=models.CharField(max_length=15)
    email=EmailField()
    hashpass=models.CharField(max_length=115)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Comic(models.Model):
    upc=models.IntegerField()
    title=models.CharField(max_length=100)
    release_date=models.CharField(max_length=100)
    uploaded_by=models.ManyToManyField(User,related_name='uploader')
    notes=models.CharField(max_length=255, default='No notes to display')
    favorite= models.ManyToManyField(User,related_name='a_fav')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Collection(models.Model):
    user=models.ForeignKey(User, related_name='creator', on_delete=CASCADE, default='0')
    col_name=models.CharField(max_length=100)
    comic=models.ManyToManyField(Comic, related_name='comic_in_col')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()







