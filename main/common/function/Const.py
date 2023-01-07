NOMAL_OK = 0  # 正常終了
FATAL_ERR = 9  # 異常終了
# Oracle Database用戻り値
DB_NOMAL_OK = 0  # 正常終了
DB_NOT_FIND = 1  # 対象データ無し
DB_LOCK = 99  # 対象データロック中
DB_TBFREETM_NOT_FIND = 2  # FreeTimeテーブル該当データなし
DB_TBCALENDER_NOT_FIND = 3  # Calenderテーブル該当データなし
DB_TBOPE_NOT_FIND = 4  # ｵﾍﾟﾚｰﾀﾃｰﾌﾞﾙ該当ﾃﾞｰﾀなし  ﾃﾞﾏﾚｰｼﾞ系関数で使用
DB_TBDEMURG_NOT_FIND = 5  # ﾃﾞﾏﾚｰｼﾞﾃｰﾌﾞﾙ該当ﾃﾞｰﾀなし ﾃﾞﾏﾚｰｼﾞ系関数で使用
DB_FATAL_ERR = 999  # FATAL_ERR

DSP_MAXCOUNT = 1000  # 一覧表示最大件数

PROGID_DELETE = "DELETE"  # 削除ﾃﾞｰﾀﾌﾟﾛｸﾞﾗﾑID

# Oracle Database用
csAREARKBN_Y = "Y"  # ｴﾘｱｺｰﾄﾞ利用区分 ﾌﾘｰﾀｲﾑ計算時、ｴﾘｱｺｰﾄﾞを利用する
csAREARKBN_N = "N"  # ｴﾘｱｺｰﾄﾞ利用区分 ﾌﾘｰﾀｲﾑ計算時、ｴﾘｱｺｰﾄﾞを利用しない
csOPEKBN_1 = "1"  # ｵﾍﾟﾚｰﾀｰ区分 船社
csOPEKBN_2 = "2"  # ｵﾍﾟﾚｰﾀｰ区分 ｺﾝｿﾘ
csTAXKBN_0 = "0"  # 課税区分 免税
csTAXKBN_1 = "1"  # 課税区分 非課税
csTAXKBN_2 = "2"  # 課税区分 課税
csCHFSNDKBN_SPC = ""  # 貨物取扱確認/見本持出確認登録送信要否区分 未送信
csCHFSNDKBN_1 = "1"  # 貨物取扱確認/見本持出確認登録送信要否区分 貨物取扱確認登録情報送信要
csCHFSNDKBN_2 = "2"  # 貨物取扱確認/見本持出確認登録送信要否区分 見本持出確認登録情報送信要
csCHFSNDFLG_SPC = ""  # 貨物取扱確認/見本持出確認登録送信区分 未送信
csCHFSNDFLG_1 = "1"  # 貨物取扱確認/見本持出確認登録送信区分 貨物取扱確認情報送信済み
csCHFSNDFLG_2 = "2"  # 貨物取扱確認/見本持出確認登録送信区分 見本持出確認登録情報送信済み
csGWSKBN_1 = 1  # Gateway選択区分 Gateway1選択
csGWSKBN_2 = 2  # Gateway選択区分 Gateway2選択
csGWSKBN_9 = 9  # Gateway選択区分 送信停止
csNVCSNDFLG_SPC = ""  # 混載貨物情報登録送信状況区分 未送信
csNVCSNDFLG_1 = "1"  # 混載貨物情報登録送信状況区分 混載親子B/L情報と関連付け登録送信済み
csNVCSNDFLG_2 = "2"  # 混載貨物情報登録送信状況区分 混載親子B/L情報と関連付け訂正送信済み
csNVCSNDFLG_3 = "3"  # 混載貨物情報登録送信状況区分 混載親子B/L情報と関連付け削除送信済み
csNVCSNDFLG_4 = "4"  # 混載貨物情報登録送信状況区分 混載子B/L情報のみ登録送信済み
csNVCSNDFLG_5 = "5"  # 混載貨物情報登録送信状況区分 混載親子B/L関連付けのみ登録送信済み
csBIAKSNDFLG_SPC = ""  # 混載子B/L個別搬入情報送信区分 未送信
csBIAKSNDFLG_1 = "1"  # 混載子B/L個別搬入情報送信区分 混載子B/L個別搬入情報送信済み
csBIAISNDFLG_SPC = ""  # 混載親B/L一括搬入情報送信区分 未送信
csBIAISNDFLG_1 = "1"  # 混載親B/L一括搬入情報送信区分 混載親B/L一括搬入情報送信済み
csBIAISNDFLG_2 = "2"  # 混載親B/L一括搬入情報送信区分 混載親B/L一括搬入情報送信済み(BIB11実施)
csNVCFREEND_S = "S"  # 混載貨物情報登録用ﾌﾘｰﾀｲﾑ期限日ｾｯﾄ位置 Shipper
csNVCFREEND_C = "C"  # 混載貨物情報登録用ﾌﾘｰﾀｲﾑ期限日ｾｯﾄ位置 Consignee
csNVCFREEND_N = "N"  # 混載貨物情報登録用ﾌﾘｰﾀｲﾑ期限日ｾｯﾄ位置 Notify
csNVCFREEND_K = "K"  # 混載貨物情報登録用ﾌﾘｰﾀｲﾑ期限日ｾｯﾄ位置 記事欄
csWORKKBN_Z = "Z"  # 雑作業区分 雑作業ｺｰﾄﾞ
csWORKKBN_D = "D"  # 雑作業区分 雑作業ｺｰﾄﾞ(ﾃﾞﾏﾚｰｼﾞ)
csWORKJKBN_0 = "0"  # 雑作業状態区分 雑作業未完了
csWORKJKBN_1 = "1"  # 雑作業状態区分 雑作業完了
csJIKOSBTCD_Z = "Z"  # 事故税関通知識別ｺｰﾄﾞ 税関へ通知を要する
csJIKOSBTCD_M = "M"  # 事故税関通知識別ｺｰﾄﾞ 税関へ通知を要しない
csSYSOUTFLG_SPC = ""  # システム外区分(NACCS) 217搬入確認登録(保税運送貨物)
csSYSOUTFLG_Z = "Z"  # システム外区分(NACCS) 217搬入確認登録(保税運送貨物)(BIB11実施)
csSYSOUTFLG_Y = "Y"  # システム外区分(NACCS) 218ｼｽﾃﾑ外搬入確認(輸入貨物)
csSYUBTKBN_1 = "1"  # 種別区分 重量単位
csSYUBTKBN_2 = "2"  # 種別区分 容積単位
csSTANKAKBN_1 = "1"  # 請求単価区分 R/T(関東用) 重量/1000or容積の大きい方
csSTANKAKBN_2 = "2"  # 請求単価区分 M3
csSTANKAKBN_3 = "3"  # 請求単価区分 TON
csSTANKAKBN_4 = "4"  # 請求単価区分 R/T(中部用) 重量or容積/1.133の大きい方
csSTANKAKBN_5 = "5"  # 請求単価区分 M3/1.133
csTUBAN_0 = 0  # 通番 ﾃﾞﾏﾚｰｼﾞ
csDIOUTFLG_SPC = ""  # D/I出力済区分 未出力
csDIOUTFLG_Y = "Y"  # D/I出力済区分 出力済
csDCALC_1 = "1"  # ﾃﾞﾏﾚｰｼﾞ計算方式 日祝除く
csDCALC_2 = "2"  # ﾃﾞﾏﾚｰｼﾞ計算方式 土日祝除く
csDCALC_3 = "3"  # ﾃﾞﾏﾚｰｼﾞ計算方式 全て含む
csNSENDFLG_Y = "Y"  # NACCS参加/不参加識別 NACCS送信対象
csNSENDFLG_N = "N"  # NACCS参加/不参加識別 NACCS送信対象外
csNSCACFLG_Y = "Y"  # NACCS B/L NO.編集識別 SCACｺｰﾄﾞ付加
csNSCACFLG_N = "N"  # NACCS B/L NO.編集識別 SCACｺｰﾄﾞ未付加
csINJKBN_0 = "0"  # 搬入状態区分 未搬入
csINJKBN_1 = "1"  # 搬入状態区分 搬入済み
csINJKBN_2 = "2"  # 搬入状態区分 搬入済み(個数"0"専用搬入)
csOUTJKBN_0 = "0"  # 搬出状態区分 未搬出
csOUTJKBN_1 = "1"  # 搬出状態区分 搬出登録有り
csOUTJKBN_2 = "2"  # 搬出状態区分 搬出済み
csOUTJKBN_3 = "3"  # 搬出状態区分 搬出済み(個数"0"専用搬出)
csBOASNDFLG_SPC = ""  # 搬出確認登録送信状況区分 未送信
csBOASNDFLG_1 = "1"  # 搬出確認登録送信状況区分 搬出確認登録情報送信済み
csFKISANKBN_1 = "1"  # ﾌﾘｰﾀｲﾑ起算日区分 搬入日起算
csFKISANKBN_2 = "2"  # ﾌﾘｰﾀｲﾑ起算日区分 搬入日翌日起算
csFCALC_1 = "1"  # ﾌﾘｰﾀｲﾑ計算方式 日祝除く
csFCALC_2 = "2"  # ﾌﾘｰﾀｲﾑ計算方式 土日祝除く
csFCALC_3 = "3"  # ﾌﾘｰﾀｲﾑ計算方式 全て含む
csDAYKBN_1 = "1"  # 曜日区分 平日
csDAYKBN_2 = "2"  # 曜日区分 土曜日
csDAYKBN_3 = "3"  # 曜日区分 日曜日
csDAYKBN_4 = "4"  # 曜日区分 祝日
csDAYKBN_9 = "9"  # 曜日区分 終了
csMTONTKBN_1 = "1"  # CT全体を対象にﾐﾆﾏﾑ屯数を適用 かつ ﾐﾆﾏﾑ屯数を満たしている
csMTONTKBN_2 = "2"  # CT全体を対象にﾐﾆﾏﾑ屯数を適用 かつ ﾐﾆﾏﾑ屯数を満たしていない
csMTONTKBN_3 = "3"  # 在庫分を対象にﾐﾆﾏﾑ屯数を適用する
csEPROUTKBN_SPC = ""  # エラー帳票出力済区分 未出力
csEPROUTKBN_Y = "Y"  # エラー帳票出力済区分 出力済
csESTATUS_W = "W"  # エラー状況 警告
csESTATUS_F = "F"  # エラー状況 致命的
csESTATUS_E = "E"  # エラー状況 エラー
csESTATUS_N = "N"  # エラー状況 正常

# その他
csDEMURRAGENM = "DEMURRAGE"  # デマレージ名称
csDEMUCKBN_A = "ALL"  # デマレージ単価区分 中部以外
csDEMUCKBN_C = "CHUBU"  # デマレージ単価区分 中部
csLOCK_ON = 1  # ロックをかけてSELECT
csLOCK_OFF = 0  # ロックをかけずにSELECT

# NACCS関連
csNACGYMCD_211 = "OLT  "  # (211)保税運送申告
csNACGYMCD_213 = "CET  "  # (213)保税運送申告審査終了
csNACGYMCD_215 = "BOA  "  # (215)搬出確認登録（保税運送貨物）
csNACGYMCD_217 = "BIA  "  # (217)搬入確認登録（保税運送貨物）
csNACGYMCD_218 = "BIB  "  # (218)システム外搬入確認登録（輸入貨物）
csNACGYMCD_22001 = "NVC01"  # (220)混載貨物情報登録（登録・訂正・削除）
csNACGYMCD_22002 = "NVC02"  # (220)混載貨物情報登録（関連付け）
csNACGYMCD_225 = "IDC  "  # (225)輸入申告
csNACGYMCD_236 = "CEC  "  # (236)輸入申告審査区分変更
csNACGYMCD_23701 = "CEA  "  # (237)輸入申告審査終了
csNACGYMCD_23702 = "CEA01"  # (237)輸入申告審査終了（強制入力）
csNACGYMCD_249 = "COW  "  # (249)保留解除
csNACGYMCD_25001 = "RCC  "  # (250)領収確認
csNACGYMCD_25002 = "RCC01"  # (250)領収確認（他官署強制入力）
csNACGYMCD_252 = "GFG  "  # (252)減額調定・不納欠損登録
csNACGYMCD_401 = "CHN  "  # (401)貨物取扱登録（内容点検）
csNACGYMCD_402 = "CHS  "  # (402)貨物取扱登録（改装・仕分け）
csNACGYMCD_404 = "CHD  "  # (404)貨物取扱許可申請
csNACGYMCD_406 = "CHE  "  # (406)貨物取扱許可申請審査終了
# csNACGYMCD_407 = "CHF  "       # (407)貨物取扱確認
csNACGYMCD_407 = "CHI  "  # (407)貨物取扱確認
csNACGYMCD_408 = "MHA  "  # (408)見本持出許可申請
csNACGYMCD_410 = "MHE  "  # (410)見本持出許可申請審査終了
csNACGYMCD_411 = "MHO  "  # (411)見本持出確認登録
csNACGYMCD_438 = "CHJ  "  # (438)貨物情報仕分け

# csNACIOCD_OLT01 = "SAC1030"    # (SAC1030)保税運送承認通知情報
# csNACIOCD_OLT02 = "SAC1050"    # (SAC1050)保税運送承認貨物情報
# csNACIOCD_OLT03 = "SAC1070"    # (SAC1070)個別運送受付情報

# csNACIOCD_OLT01 = "SAS0370"    # (SAS0370)保税運送承認通知情報
# csNACIOCD_OLT02 = "SAS0380"    # (SAS0380)保税運送承認通知情報多欄
# csNACIOCD_OLT03 = "SAS0410"    # (SAS0410)保税運送承認貨物情報
# csNACIOCD_OLT04 = "SAS0420"    # (SAS0420)保税運送承認貨物情報多欄
# csNACIOCD_OLT05 = "SAS0430"    # (SAS0430)個別運送受付情報
# csNACIOCD_OLT06 = "SAS0440"    # (SAS0430)個別運送受付情報多欄

csNACIOCD_OLT01 = "SAS0371"  # (SAS0371)保税運送承認通知情報
csNACIOCD_OLT02 = "SAS0381"  # (SAS0381)保税運送承認通知情報多欄
csNACIOCD_OLT03 = "SAS0411"  # (SAS0411)保税運送承認貨物情報
csNACIOCD_OLT04 = "SAS0421"  # (SAS0421)保税運送承認貨物情報多欄
csNACIOCD_OLT05 = "SAS0431"  # (SAS0431)個別運送受付情報
csNACIOCD_OLT06 = "SAS0441"  # (SAS0431)個別運送受付情報多欄

# csNACIOCD_IDC01 = "SAD0510"    # (SAD0510)輸入許可貨物情報


csNACIOCD_IDC01 = "SAD4311"  # (SAD4310)輸入許可貨物情報
csNACIOCD_IDC05 = "SAD4321"  # (SAD4320)輸入許可貨物情報 (2008/08/26新規追加電文)

# csNACIOCD_IDC02 = "SAD0630"    # (SAD0630)検査貨物情報（輸入）


csNACIOCD_IDC02 = "SAD4881"  # (SAD4880)検査貨物情報（輸入）
csNACIOCD_IDC04 = "SAD4901"  # (SAD4900)検査貨物情報（輸入）

csNACIOCD_IDC03 = "SAD0511"  # (SAD0511)輸入許可貨物情報（2004/01/20新規追加電文）

# csNACIOCD_CHN01 = "SAC1510"    # (SAC1510)貨物取扱（内容点検）情報
csNACIOCD_CHN01 = "SAL0020"  # (SAL0020)貨物取扱（内容点検）情報

# csNACIOCD_CHS01 = "SAC1530"    # (SAC1530)貨物取扱（改装・仕分け）情報


csNACIOCD_CHS01 = "SAL0041"  # (SAC1530)貨物取扱（改装・仕分け）情報

# csNACIOCD_CHD01 = "SAC1560"    # (SAC1560)貨物取扱許可通知情報
# csNACIOCD_CHD02 = "SAC1590"    # (SAC1590)貨物取扱許可貨物情報
csNACIOCD_CHD01 = "SAL0080"  # (SAL0080)貨物取扱許可通知情報
csNACIOCD_CHD02 = "SAL0100"  # (SAL0100)貨物取扱許可貨物情報

# csNACIOCD_MHA01 = "SAC1800"    # (SAC1800)見本持出許可通知情報
# csNACIOCD_MHA02 = "SAC1830"    # (SAC1830)見本持出許可貨物情報


csNACIOCD_MHA01 = "SAL0151"  # (SAL0150)見本持出許可通知情報
csNACIOCD_MHA02 = "SAL0171"  # (SAL0170)見本持出許可貨物情報

csNACIOCD_CHJ01 = "SAC1850"  # (SAC1850)貨物情報仕分け情報

TRACK_VANNO = "BY "

DI_MARK_PPR = 10  # DIマーク/リマーク最大行数(Page Printer)
DI_SAGYO_PPR = 5  # DI雑作業明細最大行数(Page Printer)
DI_KYOKA_PPR = 5  # DI税関許可関係最大行数(Page Printer)
DI_MARK_KSP = 10  # DIマーク/リマーク最大行数(Serial Printer)
DI_SAGYO_KSP = 5  # DI雑作業明細最大行数(Serial PRinter)
DI_KYOKA_KSP = 5  # DI税関許可関係最大行数(Serial PRinter)
