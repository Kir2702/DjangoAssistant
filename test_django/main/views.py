from django.shortcuts import render, redirect
from .forms import AnswerForm 
from main.generator import answer_script


def index(request):
    return render(request, 'main/index.html')


def samples(request):
    return render(request, 'main/samples.html')


def about(request):
    return render(request, 'main/about.html')



def authorization(request):
    return render(request, 'main/authorization.html')


def generator(request):
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            orderid = form.cleaned_data['orderid']
            answ = answer_script.generating_response(orderid)
            raw = 1
            for line in answ:
                if ord(line) == 10:
                    raw = raw+1
            data = {'form': form, 'raw': raw, 'answ': answ}
    else:
        form = AnswerForm()
        data = {'form': form, 'raw': 3, 'answ': ''}
    return render(request, 'main/generator.html', data)


        
        


    
    
    
    
    
    
