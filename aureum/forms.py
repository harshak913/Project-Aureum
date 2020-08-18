from django import forms

class MyForm(forms.Form): #Note that it is not inheriting from forms.ModelForm
    a = forms.CharField(max_length=20)
