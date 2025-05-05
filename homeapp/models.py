from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.
class Userprofile(AbstractUser):
    is_director = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)  # For Maganjo branch
    is_manager_2 = models.BooleanField(default=False)  # For Matugga branch
    is_salesagent = models.BooleanField(default=False)  # For Maganjo branch
    is_salesagent_2 = models.BooleanField(default=False)  # For Matugga branch
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50)
    phone_number = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=50)
    gender = models.CharField(blank=False)
     
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    
    
class Branch(models.Model):
    #location = models.ForeignKey(Category,null=True, blank=True, on_delete=models.CASCADE)
    branch_name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.branch_name

class Stock(models.Model):
    Name_of_produce = models.CharField(max_length=100, null=True)
    Produce_type = models.CharField(choices=[("Internal","Internal"), ("External","External")] ,blank=True, null=True)
    Date = models.DateField(auto_now_add=True)
    Tonnage_in_kgs = models.IntegerField(blank=False, default=0)
    total_quantity = models.IntegerField(default=0,blank=True, null=True)
    Cost = models.IntegerField(blank=False, default=0)
    Unit_price = models.IntegerField(blank=True, null=True)
    Dealer_name = models.CharField(blank=False, default=0)
    Branch = models.ForeignKey(Branch,blank=True, null=True, on_delete=models.CASCADE)
    #current_stock = models.IntegerField(blank=True, null=True)
    Contact = models.IntegerField(default=0, blank=False)
    received_quantity = models.IntegerField(default=0,blank=True,null=True)


    def __str__(self):
        return self.Name_of_produce
    

class Sale(models.Model):
    Name_of_produce = models.ForeignKey(Stock, blank=True, null=True, on_delete=models.CASCADE)
    item_name = models.CharField(blank=True, null=True)
    Tonnage_in_kgs = models.IntegerField(blank=False)
    #Unit_price = models.ForeignKey(Stock,on_delete=models.CASCADE, blank=True, null=True)
    Amount_paid = models.IntegerField(default=0,blank=False)
    Branch = models.ForeignKey(Branch, blank=True, null=True, on_delete=models.CASCADE)
    Sales_agent_name = models.CharField(blank=False)
    Date_time = models.DateTimeField(auto_now_add=True)
    Name_of_buyer = models.CharField(blank=True)
    method_of_payment = models.CharField(choices=[("Cash", "Cash"), ("Credit", "Credit")],blank=True, null=True)

    def get_amount_paid(self):
        amount_paid = self.Tonnage_in_kgs * self.Name_of_produce.Unit_price
        return int(amount_paid)
    
    def get_change(self):
        change = self.get_amount_paid() - self.Amount_paid
        return (int(change))

    def __str__(self):
        return self.Name_of_buyer
    

class Deferred_Payment(models.Model):
    Name_of_buyer = models.CharField(blank=True, null=True)
    Nin = models.CharField(blank=False, unique=True)
    Location = models.CharField(blank=False)
    Amount_due = models.IntegerField(blank=False, default=0)
    Contact = models.IntegerField(blank=False, null=False)  # Making contact required and not nullable
    Sales_agent_name = models.CharField(blank=False)
    Due_date = models.DateField(auto_now_add=True)
    Produce_name = models.CharField(blank=False)
    Produce_type = models.CharField( blank=False)
    Branch = models.ForeignKey(Branch, blank=True, null=True, on_delete=models.CASCADE)
    Tonnage = models.IntegerField(blank=False,default=0)
    Date_of_dispatch = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.Nin

