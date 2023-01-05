def ContCheck(strArgVan):
    strVanChr = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                 "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    intVanNum = [10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 1, 2, 3,
                 4, 5, 6, 7, 8, 9, 0]
    intAns = 0
    if strArgVan == "":
        return 9
    if strArgVan[:3] == "BY ":
        return 0
    if len(strArgVan) < 9:
        return 1
    for i in range(9, 0, -1):
        if strArgVan[i] in strVanChr:
            intAns = intAns + intVanNum[strVanChr.index(strArgVan[i])] * (2 ** i)
        elif strArgVan[i] == " ":
            break
    if intAns % 11 == 10:
        if strArgVan[10] in ["0", "A"]:
            return 0
        else:
            return 2
    else:
        if strArgVan[10] == intAns % 11:
            return 0
        else:
            return 2
