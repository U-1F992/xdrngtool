from datetime import timedelta

# https://github.com/yatsuna827/xddb/blob/dc619a3ec909a44f33ac5bd7df6dcc9e0e807977/src/xddb/client.py#L39-L53
PLAYER_BASE_HP: list[tuple[int, int]] = [
    (322, 340),
    (310, 290),
    (210, 620),
    (320, 230),
    (310, 310),
]
ENEMY_BASE_HP: list[tuple[int, int]] = [
    (290, 310),
    (290, 270),
    (290, 250),
    (320, 270),
    (270, 230),
]

# 指定されない場合に使用するTSV
DEFAULT_TSV = 0x10000

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
# 主人公の腰振りにかかる消費数
ADVANCES_BY_WATCHING_STEPS = 2
