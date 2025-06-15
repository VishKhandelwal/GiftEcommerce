from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import ShortURL

def redirect_short_url(request, code):
    url_obj = get_object_or_404(ShortURL, code=code)
    return redirect(url_obj.target_url)


# Create your views here.
