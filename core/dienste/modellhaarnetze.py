# -*- coding: utf-8 -*-
"""Modellhaarnetze — Haar und Bart der Haar-Engine als Anzeigenetz neben einem gespeicherten Genesis-Modell (23.11.2026).

Edgar, 23.11.2026: „beim Speichern sollen zumindest Haare, Bart, Haut mitgehen“; zum Vorschlag, statt des Bibliotheksstücks die Strähnen der Engine zu speichern: „mach alles“.
Die Ergebniskarte von Mesh-Genesis und Foto-Genesis zeigt Haar und Bart (Weg z, „Kleiderbibliothek“) als das Anzeigenetz, das die Haar-Engine gebaut hat (`haar_Bart`:
Karten mit Deckkraftbild und Punktfarben, Kopfhaut-Kappe als zweites Material, eigene Hautgewichte auf den Knochen der Figur). Bis dahin trug das Modell das Bibliotheksstück,
nach dem die Engine gewählt hatte (`kennung`, am Zauberer „Longhair-prop“) — ein anderes Haar. Ein Stück der Garderobe kann das Anzeigenetz nicht werden: eine DSON-Datei trägt
keine Punktfarben, `G9dsonschreiber` schreibt eine Materialgruppe, und das Haar des Zauberers hat 2,2 Mio. Punkte. Darum geht das Anzeigenetz selbst mit:

    data/models/Haarnetze/<Stück>_<Stand>/anzeige/{netz.pt bzw. netz.npz, materialien.json, bilder/}

Der Ordner heißt nach Stück und Stand der Quelle (Pfad, Zeit und Größe der Netzdatei), nicht nach dem Modell: Umbenennen und „Modell speichern“ unter neuem Namen behalten die
Adresse, und kein anderes Modell überschreibt ihn (gleicher Stand = gleicher Inhalt; eine neu gerechnete Frisur bekommt einen neuen Ordner). `materialien.json` wird zuletzt kopiert —
ohne sie gilt der Ordner als unfertig (`ordner`) und das nächste Speichern kopiert neu. Ein Probelauf (`ziel_ordner`) kopiert nichts und behält die Adresse des Tests.

Ins Modell kommt `figur.haarnetze = {knochen, ruhezentren, stuecke: [{id, name, art, adresse}]}`: die Knochennamen in der Reihenfolge der Gewichte und die Ruhegelenke der Figur, auf der
die Engine gebaut hat (`form_<g>/kinematik.json`, wie die Abspielleiste der Testseite, `Meshgenesisbewegungsfigur.rahmen`). Jede Seite mit einer Genesis-Figur bindet es mit dem Code der
Testseite an das Skelett (`genesis9haarnetze.js` → `Meshgenesisbewegungskleid.binden`); ausgeliefert wird es wie ein Stück eines Tests (`G9haarnetzapi`).
"""

import hashlib
import json
import logging
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from django.conf import settings

from ..daten.modellpfad import Modellpfad
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402

logger = logging.getLogger('core')

__all__ = ['Modellhaarnetze']


class Modellhaarnetze:
    ORDNER = 'Haarnetze'
    ADRESSE = '/api/character/genesis9-figur/haarnetz/'
    NAME = re.compile(r'^[a-z0-9_]{1,64}_[0-9a-f]{12}$')
    ID = re.compile(r'^[a-z0-9_]{1,64}$')
    #: Marken im Eintrag des Wegs, die die Haar-Engine setzt (`Haarmethode`, `Bartmethode`) — ohne sie ist das Anzeigenetz das Bibliotheksstück selbst, und dessen Kennung genügt
    ENGINE = ('haar_engine', 'bart_engine')
    #: Zahl der Stellen der Ruhegelenke (wie `Meshgenesistest.daten`)
    STELLEN = 6

    @classmethod
    def wurzel(cls):
        return Path(settings.HUMANBODY_MODELS_DIR) / cls.ORDNER

    @classmethod
    def ordner(cls, name):
        """`Haarnetze/<name>` — der Ordner mit `anzeige/` für `Meshgenesisflaechennetz` — oder None (unzulässiger Name, unfertig oder fehlt)."""
        name = str(name or '')
        if not cls.NAME.match(name) or Modellpfad.geprueft(cls.wurzel(), name, '') is None:
            return None
        p = cls.wurzel() / name
        return p if (p / 'anzeige' / 'materialien.json').is_file() else None

    @classmethod
    def stueck(cls, kleider_ordner, st, wahl):
        """Haar oder Bart der Zeile `st` auf dem Weg `wahl`, wenn die Engine es gebaut hat und ein Anzeigenetz liegt: `{id, name, art, quelle, netz}` (`quelle` = Ordner mit `anzeige/`,
        `netz` = Adresse des Tests), sonst None."""
        e = st.get(wahl) if isinstance(st.get(wahl), dict) else {}
        if st.get('art') != 'haar' or not any(e.get(m) for m in cls.ENGINE) or not cls.ID.match(str(st.get('id') or '')):
            return None
        quelle = Path(kleider_ordner) / wahl / st['id']
        if not Npztorch.da(quelle / 'anzeige' / 'netz.npz') or not (quelle / 'anzeige' / 'materialien.json').is_file():
            return None
        return {'id': st['id'], 'name': st.get('name') or st['id'], 'art': 'haar', 'quelle': str(quelle), 'netz': e.get('netz')}

    @classmethod
    def feld(cls, stuecke, kleider_ordner, geschlecht, sichern):
        """`figur.haarnetze` aus den Stücken von `stueck` oder None (keine). `sichern`: neben das Modell kopieren (sonst die Adresse des Tests, Probelauf)."""
        if not stuecke:
            return None
        kin = json.loads((Path(kleider_ordner).parent / ('form_%s' % geschlecht) / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        aus = []
        for s in stuecke:
            adresse = cls.sichern(s['id'], s['quelle']) if sichern else s.get('netz')
            if adresse:
                aus.append({'id': s['id'], 'name': s['name'], 'art': s['art'], 'adresse': adresse})
        return {'knochen': [k['name'] for k in kin], 'ruhezentren': [[round(float(w), cls.STELLEN) for w in k['zentrum']] for k in kin], 'stuecke': aus} if aus else None

    @classmethod
    def sichern(cls, stueck_id, quelle):
        """`quelle/anzeige` nach `Haarnetze/<Stück>_<Stand>/anzeige` (schon da: nichts) → Adresse ohne Schrägstrich am Ende (`Meshgenesisflaechennetz.holen` hängt `netz/` an)."""
        anzeige = Path(quelle) / 'anzeige'
        netz = Npztorch.datei(anzeige / 'netz.npz')
        stand = netz.stat()
        marke = hashlib.sha1(('%s|%d|%d' % (netz.resolve(), stand.st_mtime_ns, stand.st_size)).encode('utf-8')).hexdigest()[:12]
        name = '%s_%s' % (stueck_id, marke)
        if cls.ordner(name) is None:
            ziel = cls.wurzel() / name / 'anzeige'
            (ziel / 'bilder').mkdir(parents=True, exist_ok=True)
            cls._kopie(netz, ziel / netz.name)
            for bild in sorted((anzeige / 'bilder').glob('*')) if (anzeige / 'bilder').is_dir() else ():
                if bild.is_file():
                    cls._kopie(bild, ziel / 'bilder' / bild.name)
            cls._kopie(anzeige / 'materialien.json', ziel / 'materialien.json')          # zuletzt: erst jetzt gilt der Ordner (`ordner`)
            logger.info('Haarnetz %s: %s → %s (%.1f MB)', stueck_id, anzeige, ziel, stand.st_size / 2 ** 20)
        return '%s%s' % (cls.ADRESSE, quote(name))

    @staticmethod
    def _kopie(quelle, ziel):
        """Ganz oder gar nicht: erst `<ziel>.teil`, dann umbenennen."""
        teil = ziel.with_name(ziel.name + '.teil')
        shutil.copyfile(quelle, teil)
        os.replace(teil, ziel)
