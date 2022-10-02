from typing import Optional

from lcg.gc import LCG
from xddb import generate_quick_battle

def _generate_quick_battle(lcg: LCG, tsv: Optional[int]):
    """（暫定）generate_quick_battleで、tsvが渡された場合にもSet[int]を返す

    Args:
        lcg (LCG): _description_
        tsv (Optional[int]): _description_

    Returns:
        _type_: _description_
    """
    if tsv is None:
        return generate_quick_battle(lcg)
    else:
        s = set([tsv])
        p, e, h = generate_quick_battle(lcg, tsv)
        return p, e, h, s
    