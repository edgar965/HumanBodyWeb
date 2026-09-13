# -*- coding: utf-8 -*-
u"""Ein Modul je Fassung — der Changelog wächst um Dateien, nicht um Zeilen.

Jede Fassung liegt in `v0NN.py` als Wörterbuch `FASSUNG` (Schema wie
djangoBases `manual_versions`: `version`, `date`, `title`, `author`,
`body_md`). `versionsliste.py` reiht sie hier neueste zuerst auf.
"""
from .v057 import FASSUNG as V057
from .v058 import FASSUNG as V058
from .v059 import FASSUNG as V059
from .v060 import FASSUNG as V060

#: Neueste zuerst — so rendert die Seite den Block.
ALLE = [V060, V059, V058, V057]
