

def MsgDspError(request, type, TitleStr, MsgStr):
    request.context["MsgDsp"] = {"type": type, "title": TitleStr, "msg": MsgStr}
