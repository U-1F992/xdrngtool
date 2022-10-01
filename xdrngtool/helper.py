from typing import Optional

from lcg.gc import LCG
from xddb import generate_quick_battle

def _generate_quick_battle(lcg: LCG, tsv: Optional[int]):
    if tsv is None:
        return generate_quick_battle(lcg)
    else:
        return generate_quick_battle(lcg, tsv)
    