# -*- coding: utf-8 -*-
"""Meshgenesistestliste — die Tests von Mesh-Genesis mit ihrem Stand, für Listen und Seiten
(aus `Meshgenesistest.alle` gelöst, 23.11.2026).

WARUM (23.11.2026, Edgar: „mach weiter mit den optimierungen“): `/foto-genesis/`, `/mesh-genesis/` und jede
Testseite `/mesh-genesis/test/<kennung>/` lasen alle 222 Tests, und je Test lud `Meshgenesistest.form` die
`form.npz` mit torch auf die Karte — nur um zu wissen, OB es die vorhergesagte Form gibt. Gemessen
(`ProjektTemp/_wegwerf/ladezeit/liste_profil.py`): `Fotogenesistabellen.alle` warm 876–939 ms, im Profil
`form` 887 von 1.456 ms; curl bis zum ersten Byte /foto-genesis/ 0,95–1,3 s, /mesh-genesis/test/… 0,76–1,05 s.
Jetzt fragt die Liste nur `Meshgenesistest.form_da` (dieselben Prüfungen, ohne Lesen), und wer einzelne Tests
braucht (Foto-Genesis die Tests seiner Jobs, die Testseite ihren einen), liest nur diese (`eintraege`).
Gleichstand geprüft mit `_wegwerf/ladezeit/testliste_gleich.py`.

Die Kennung in `test.json` ist die des Ordners — außer bei beiseitegelegten Ständen
(`<kennung>_beiseite_<Zeit>`), die beide Wege überspringen (geprüft an allen 232 Dateien).
"""

import json

from KoerperKI_alle.npztorch import Npztorch

from .meshgenesisaposewahl import Meshgenesisaposewahl
from .meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesistestliste']


class Meshgenesistestliste:

    @classmethod
    def alle(cls, mit_tripo=False, ohne=()):
        """Die Tests mit ihrem Stand (`test.json`), nach Name; ein unlesbarer steht mit Fehler in der Liste
        statt zu fehlen. `figur`/`geschlecht` sind die eingestellten. `mit_tripo`: auch die Tripo-Jobs (Ordner
        mit `ziel/`), markiert mit `tripo` — nur für die Übersicht des Reiters „Test“. `ohne`: diese Kennungen
        gar nicht erst lesen (die Testtabelle von /mesh-genesis/ zeigt 22 von 219, `Meshgenesisjobtest`)."""
        ordner = Meshgenesistest.ordner()
        if not ordner.is_dir():
            return []
        weg, ohne = Meshgenesisaposewahl.gewaehlt(), set(ohne)
        eintraege = (cls._eintrag(p, weg, mit_tripo) for p in sorted(ordner.iterdir())
                     if '_beiseite_' not in p.name and p.name not in ohne)
        return sorted((e for e in eintraege if e is not None), key=lambda i: str(i.get('name', '')).lower())

    @classmethod
    def eintraege(cls, kennungen, mit_tripo=False):
        """{Kennung: Eintrag wie in `alle`} nur der genannten Tests; unbekannte, unzulässige und
        beiseitegelegte fehlen."""
        weg, aus = Meshgenesisaposewahl.gewaehlt(), {}
        for kennung in dict.fromkeys(k for k in kennungen if k):
            if not Meshgenesistest.KENNUNG.match(str(kennung)) or '_beiseite_' in kennung:
                continue
            eintrag = cls._eintrag(Meshgenesistest.ordner() / kennung, weg, mit_tripo)
            if eintrag is not None:
                aus[kennung] = eintrag
        return aus

    @staticmethod
    def _eintrag(p, weg, mit_tripo):
        """Der Eintrag eines Testordners — oder None (kein Test, oder ein Tripo-Job ohne `mit_tripo`)."""
        if not (p / 'test.json').is_file():
            # angelegt, noch nicht gerechnet (`anlage.json`) — steht in der Liste, damit man ihn öffnen und
            # „Rechnen“ drücken kann
            return dict(Meshgenesistest.anlage(p), tripo=False) if (p / 'anlage.json').is_file() else None
        # Trainingspaare (Ziel unter `ziel/`) sind seit 19.10.2026 Trainingsdaten, keine Tests (Edgar: „die
        # sollst du als nächstes trainieren, lösche sie aus den Testläufen“); ihr Ordner bleibt
        # (MIA-Grundhaltung des Tripo-Netzes = Eingang der Trainingswolke), die Seite
        # `/mesh-genesis/test/<paar>/` bleibt über die Adresse erreichbar. In der Übersicht stehen sie seit
        # 23.10.2026 wieder (Edgar: „Ich sehe die anderen Jobs nicht in der Übersicht“ — die Kostüm-Ergebnisse
        # liegen auf ihren Testseiten).
        tripo = (p / 'ziel' / 'ziel.json').is_file()
        if tripo and not mit_tripo:
            return None
        e = Meshgenesistest.endung(p, weg)
        try:
            test = json.loads((p / ('test%s.json' % e)).read_text(encoding='utf-8'))
            info = Meshgenesistest._mit_name(p, test)
            g = info['geschlecht'] = Meshgenesistest.geschlecht(p, info)
            form = Meshgenesistest.form_da(p, info, g)
            info['figur'] = 'Form (vorhergesagt)' if form else Meshgenesistest.wahl(p, info, g, e)[0]
        except (OSError, ValueError) as fehler:
            info = {'kennung': p.name, 'name': p.name, 'fehler': str(fehler)}
        info['fertig'] = bool(info.get('figur')) and Npztorch.da(p / ('vorschau%s.glb' % e))
        info['tripo'] = tripo
        return info
