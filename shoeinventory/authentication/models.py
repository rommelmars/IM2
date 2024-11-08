from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Shoe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10)
    image = models.ImageField(upload_to='images/', null=True, blank=True)  
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # TIG LINK SA USER
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        # total amount sa tanan
        self.total_amount = self.shoe.price * self.quantity_sold

        # updte ni inventory
        if self.shoe.stock >= self.quantity_sold:
            self.shoe.stock -= self.quantity_sold
            self.shoe.save()  # Save the stock adjustment

            super().save(*args, **kwargs)  # tig save sa sales
        else:
            raise ValueError("Insufficient stock for this sale")