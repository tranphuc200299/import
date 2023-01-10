def OraErrorB(EData):
    try:
        pass
    except psycopg2.errors:
        if psycopg2.errors == "23505":
            raise "ＤＢ読み込みエラー発生" & vbCrLf & vbCrLf & "該当データは他で使用中です。"
        e
