import os
from main.common.function.Const import  rtnProcOK, rtnProcNG
dir_path = os.path.dirname(os.path.realpath(__file__))


def GetArguments(EData, WkRPos, WkFPos, WkEPos, WkArgs):
    try:
        argNaccsFile = WkArgs[WkFPos - 1: 2 * WkFPos - 1][4].strip()
        argOKFile = WkArgs[WkFPos - 1: WkEPos - 1][4].strip()
        argNGFile = WkArgs[WkFPos - 1: WkEPos + WkFPos - 1][4].strip()
        return rtnProcOK
    except:
        # EData.ErrCd = Err
        # EData.ErrData = Error(Err)
        # EData.EPlace = "GetArguments"
        return rtnProcNG

def GetArguments2(EData, WkArgs):
