from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Customer(models.Model):  # cascde means if model is deleted the relationship is also deleted
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)  # extending this model to cater for users
    name = models.CharField(max_length=500, null=True)
    phone = models.IntegerField(null=True)
    email = models.EmailField(null=True)
    profile_pic = models.ImageField(default='car.jpg', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.name} {self.email}'


class Tag(models.Model):
    name = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY = (
        ('Indoor', 'Indoor'),
        ('Out Door', 'Out Door'),
    )
    tag = models.ManyToManyField(Tag)
    name = models.CharField(max_length=500, null=True)
    price = models.FloatField(null=True)
    category = models.CharField(max_length=500, null=True, choices=CATEGORY)
    description = models.CharField(max_length=500, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=500, null=True, choices=STATUS)
    note = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.product.name
