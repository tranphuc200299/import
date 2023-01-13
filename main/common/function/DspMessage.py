import json


def MsgDspError(request, TitleStr, MsgStr):
    request.context["MsgDsp"] = json.dumps({"type": "Err", "title": TitleStr, "msg": MsgStr})


def MsgDspInfo(request, TitleStr, MsgStr):
    request.context["MsgDsp"] = json.dumps({"type": "Info", "title": TitleStr, "msg": MsgStr})


def MsgDspWarning(request, TitleStr, MsgStr):
    request.context["MsgDsp"] = json.dumps({"type": "Warn", "title": TitleStr, "msg": MsgStr})
