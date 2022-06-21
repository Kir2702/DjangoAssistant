from django import forms


class AnswerForm(forms.Form):
    orderid = forms.CharField(label='ID заказа', max_length=8)    