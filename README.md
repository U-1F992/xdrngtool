# xdrngtool

ポケモンXD乱数調整用関数群

## Reference

- [xddb](https://github.com/yatsuna827/xddb)
- [XDSeedSorter](https://github.com/mukai1011/XDSeedSorter)

## Pythonわからん

```powershell
# test
pip install -e .
poetry run python .\tests\test_helper.py
```

`lcg.py`は[xddb](https://github.com/yatsuna827/xddb)からお借りしています。

Python向けの疑似乱数生成器ライブラリが出たらそれに乗り換えます。

```powershell
Invoke-WebRequest https://github.com/yatsuna827/xddb/raw/main/src/xddb/lcg.py -o .\xdrngtool\lcg.py
# or like this
# curl -L
```
