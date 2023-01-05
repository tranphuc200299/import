from django.http import JsonResponse


class Response(object):
    def __init__(self, request):
        self.request = request

    def json_response_textchange(self, id_show_data) -> JsonResponse:
        if type(id_show_data) is list:
            data = {
                "gSetField": self.request.context["gSetField"],
            }
            for show_data in id_show_data:
                data[show_data] = self.request.context[show_data]
        else:
            data = {
                id_show_data: self.request.context[id_show_data],
                "gSetField": self.request.context["gSetField"],
            }
        return JsonResponse(data)
