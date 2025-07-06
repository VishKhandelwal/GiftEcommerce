from django.shortcuts import render

def faq_view(request):
    return render(request, 'support/faq.html')

def contact_view(request):
    return render(request, 'support/contact.html')
