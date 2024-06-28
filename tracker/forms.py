from datetime import datetime
from django.core.exceptions import ValidationError
from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Transaction
        fields = ("category", "type", "amount", 'date')
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date > datetime.now().date():
            raise ValidationError("The date cannot be in the future.")
        return date
    
    def clean_amount(self):
        amount= self.cleaned_data.get('amount')
        if amount < 1:
            raise forms.ValidationError("The Amount can not be less than 1!!")
        return amount
