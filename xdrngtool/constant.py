from datetime import timedelta

# 最短の待機時間
# 戦闘にファイヤーが登場するまで、および降参してから消費が止まるまでにはラグがあるため、短すぎると制御が難しいです。
MINIMUM_WAIT_TIME = timedelta(minutes=1)

# 最長の待機時間
# 待機が長すぎると初期seed厳選をする意味がないですが、短く設定し過ぎると厳選に時間がかかりすぎます。
# 経験上3時間ぐらいがいい塩梅です。
MAXIMUM_WAIT_TIME = timedelta(hours=3)

# 待機時間から天引きする時間
# 短い方が戦闘後の消費行動を少なくできますが、先述の理由で短くし過ぎると消費しすぎるなどの不具合が発生します。
LEFTOVER_WAIT_TIME = timedelta(minutes=1)

# いますぐバトルにファイヤーを出した場合の消費数/秒
# 一般的には3713.6と言われていますが（出典不明）、3842程度で上手くいきます。
ADVANCES_PER_SECOND_BY_MOLTRES = 3842

# 振動設定変更の消費数
ADVANCES_BY_CHANGING_SETTING = 40
# レポートにかかる消費数
ADVANCES_BY_WRITING_REPORT = 63
