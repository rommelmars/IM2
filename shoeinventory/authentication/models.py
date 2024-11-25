from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Shoe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # Add category

    def __str__(self):
        return self.name

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shoe = models.ForeignKey(Shoe, on_delete=models.SET_NULL, null=True, blank=True)
    shoe_name = models.CharField(max_length=100, blank=True)  # Stores the shoe name for deleted shoes
    quantity_sold = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        # Store the shoe name if the shoe is available
        if self.shoe:
            self.shoe_name = self.shoe.name
            self.total_amount = self.shoe.price * self.quantity_sold

            # Ensure sufficient stock
            if self.shoe.stock >= self.quantity_sold:
                self.shoe.stock -= self.quantity_sold
                self.shoe.save()
            else:
                raise ValueError("Insufficient stock for this sale.")
        elif not self.shoe_name:
            # Raise an error if no shoe or name is available
            raise ValidationError("Shoe reference is missing for this sale.")

        super().save(*args, **kwargs)  # Call the parent save method

    def __str__(self):
        return f"Sale of {self.quantity_sold} {self.shoe_name if self.shoe_name else 'Deleted Shoe'}"
    
