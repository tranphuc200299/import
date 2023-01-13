import json


def MsgDspError(request, type, TitleStr, MsgStr):
    request.context["MsgDsp"] = json.dumps({"type": type, "title": TitleStr, "msg": MsgStr})
