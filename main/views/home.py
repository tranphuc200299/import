from django.shortcuts import render

from main.common.decorators import update_context


@update_context()
def home(request):
    return render(request, "home.html", request.context)
