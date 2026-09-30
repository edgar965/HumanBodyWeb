# -*- coding: utf-8 -*-
"""Ein Modul je Fassung — der Changelog wächst um Dateien, nicht um Zeilen.

Jede Fassung liegt in `v0NN.py` als Wörterbuch `FASSUNG` (Schema wie
djangoBases `manual_versions`: `version`, `date`, `title`, `author`,
`body_md`). `versionsliste.py` reiht sie hier neueste zuerst auf.
"""

from .v057 import FASSUNG as V057
from .v058 import FASSUNG as V058
from .v059 import FASSUNG as V059
from .v060 import FASSUNG as V060
from .v061 import FASSUNG as V061
from .v062 import FASSUNG as V062
from .v063 import FASSUNG as V063
from .v064 import FASSUNG as V064
from .v065 import FASSUNG as V065
from .v066 import FASSUNG as V066

#: Neueste zuerst — so rendert die Seite den Block. (`v064.py` lag seit dem
#: 24.09.2026 im Ordner, stand aber nicht in dieser Liste — Hilfe → Versionen
#: zeigte 0.64 deshalb nicht; `test_versionshistorie` fand es am 30.09.)
ALLE = [V066, V065, V064, V063, V062, V061, V060, V059, V058, V057]
