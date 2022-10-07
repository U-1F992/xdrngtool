# xdrngtool

ポケモン XD 乱数調整用関数群

```
>>> import xdrngtool
>>> print(xdrngtool.title_logo)

                                            /^^        
 ___       _      __                /^^   /^^/^^^^^    
| . \ ___ | |__ _/_/._ _ _  ___ ._ _ /^^ /^^ /^^   /^^ 
|  _// . \| / // ._>| ' ' |/ . \| ' |  /^^   /^^    /^^
|_|  \___/|_\_\\___.|_|_|_|\___/|_|_|/^^ /^^ /^^    /^^
        Gale    of    Darkness      /^^   /^^/^^   /^^ 
  -----===========================/^^========/^^^^^    
```

## Usage

`.\tests\test_execute.py`も確認してください。

---

### 操作の注入

`run`メソッドを持つ、以下のクラスを定義してください。クラス名は自由ですが、引数名および型、戻り値の型は固定です。

それぞれの操作は、次の入力ができるようになるまでをワンセットとしてください。ある操作が実行された後、即座に次の操作が呼ばれても正常に動くよう、適切な待機処理などを挟んでください。

```python
class TransitionToQuickBattle():
    """リセットし、1回いますぐバトル（さいきょう）を生成した画面まで誘導する。
    """
    def run(self):
        pass

class GenerateNextTeamPair():
    """現在のいますぐバトル生成結果を破棄し、再度生成する。
    """
    def run(self) -> TeamPair:
        pass

class EnterWaitAndExitQuickBattle():
    """「このポケモンで　はじめてもよいですか？」「はい」からいますぐバトルを開始し、降参「はい」まで誘導。timedelta時間待機した後、いますぐバトルを降参し、1回いますぐバトルを生成する。
    """
    def run(self, td: timedelta):
        pass

class SetCursorToSetting():
    """いますぐバトル生成済み画面から、「せってい」にカーソルを合わせる。
    """
    def run(self):
        pass

class ChangeSetting():
    """「せってい」にカーソルが合った状態から、設定を変更して保存、「せってい」にカーソルを戻す。
    """
    def run(self):
        pass

class Load():
    """「せってい」にカーソルが合った状態からロードし、メニューを開き「レポート」にカーソルを合わせる。
    """
    def run(self):
        pass

class WriteReport():
    """「レポート」にカーソルが合った状態から、レポートを書き、「レポート」にカーソルを戻す。
    """
    def run(self):
        pass
```

pokecon で使用する場合は、`__init__`で PythonCommand を与えればよいでしょう。

```python
class TransitionToQuickBattle():
    def __init__(self, command):
        self.__command = command
    def run(self):
        self.__command.press()
        # ...

class HogeCommand(ImageProcPythonCommand):
    def do(self):
        transition_to_quick_battle = TransitionToQuickBattle(self)
        # ...
```

これらの操作を所定の順番でタプルに詰め、`execute_automation`に与えます。

```python
operations = (
    TransitionToQuickBattle(),
    GenerateNextTeamPair(),
    EnterWaitAndExitQuickBattle(),
    SetCursorToSetting(),
    ChangeSetting(),
    Load(),
    WriteReport(),
)

execute_automation(operations, target_seeds, tsv, advances_by_opening_items)
```

### 目標seed

関数の終了時に、そのseedに合っている状態になります。強制消費は事前に調査し、差し引いたseedを入力してください。

### TSV

`None`でも構いませんが、正確に指定したほうがいいです。いますぐバトルの生成予測に齟齬が生じ、消費経路の再計算が発生する可能性があります。

ライブラリ側で対処しているため通常は問題ありませんが、運悪く消費中の最後の数回で再計算が発生すると、経路の修正が利かずまずそうです（超レアなケースなので、もし遭遇したら報告をお待ちしています）。

### もちもの消費

`advances_by_opening_items`は「もちもの」を開閉する操作にかかる消費数です。設定によって、終了時の状況が異なります。関数以降に自動操作を続ける場合は注意してください。

| 設定値     | 動作                                                                                                                                                                 |終了位置|
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |---|
| `None`     | フィールドに NPC 等不定消費要素があり、ロード後の seed 調整が不可能な場合に使用します。<br>ロードせず、振動設定の変更（40 消費）のみで seed の調整を行います。       |メニュー画面（カーソルが「せってい」に合っている状態）|
| `None`以外 | フィールドに NPC 等不定消費要素がなく、ロード後に seed 調整が可能な場合に使用します。<br>ロードを挟み、振動設定の変更とレポート（63 消費）で seed の調整を行います。 |フィールド（メニューが開き、カーソルが「レポート」に合っている状態）|

## Reference

- [xddb](https://github.com/yatsuna827/xddb)
- [XDSeedSorter](https://github.com/mukai1011/XDSeedSorter)

## Python わからん

```powershell
# test
pip install -e .
poetry run python .\tests\test_hoge.py
```
