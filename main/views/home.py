from django.shortcuts import render

from main.common.decorators import update_context, load_cfs_ini


@update_context()
@load_cfs_ini()
def home(request):
    return render(request, "home.html", request.context)
