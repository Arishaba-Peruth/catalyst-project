from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm

class AddStockForm(ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'

class AddSaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'

class AddDeferred_PaymentForm(ModelForm):
    class Meta:
        model = Deferred_Payment
        fields = '__all__'

class UpdateStockForm(ModelForm):
    class Meta:
        model = Stock
        fields = ['received_quantity']

class UserCreation(UserCreationForm):
    class Meta:
        model = Userprofile
        fields = '__all__'

    def save(self, commit=True):
        user = super(UserCreation,self).save(commit=False)
        if commit:
            user.is_active = True
            user.is_staff = True
            user.save()
        return user
