from django.shortcuts import render

from main.common.decorators import update_context
from main.middleware.exception.exceptions import RuntimeException
from main.middleware.exception.message import E00001


@update_context()
def login(request):
    raise RuntimeException(error_code=E00001, message="失敗しました。システム管理者に連絡してください")
    return render(request, "login.html")
