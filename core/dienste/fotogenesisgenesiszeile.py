# -*- coding: utf-8 -*-
"""Fotogenesisgenesiszeile — die dritte Zeile der Jobseite jedes Tests aus Fotos (04.11.2026; erst nur PSHuman-Jobs, abends Edgar: „passe sie ans neue Layout an“).

Edgar: „3. Zeile: Genesis - Mesh3d-AI, Genesis - 2d3dai (aus Fotos), Genesis Ergebnis (mes3d-ai)“. Feld 2 ist
das Feld „Genesis-Modell“ der Seite (`daten.test`); hier die beiden Felder aus dem Mesh-Genesis-Test zum
Netz (job.json `meshgenesis_test`; jeder Job steht für sich, 04.11.2026, Edgar: „die jobs sollen immer unabhängig sein“):

    meshgenesis   Genesis – Mesh-Genesis: die Einpassung ohne KI, Zeile 1 der Testseite (`Meshgenesismeshanpassung`)
               → `/api/meshgenesis/test/<k>/meshanpassung/`
    ergebnis   Genesis-Ergebnis (Mesh-Genesis): die Figur des fertigen Tests (Figur aus Zeile 1, Haut, Kleider)
               → `/api/meshgenesis/test/<k>/` (wie `Fotogenesistestfigur` sie baut)
    figur      Testdaten mit `figur_genesis` (`/api/meshgenesis/test/<k>/`), sobald die Form der Zeile 1 steht
               (`form_<g>/modell.json`: Regler der Einpassung, Versatz als eigene Morphs) — Abspielleiste
               und Export von Feld 1 (04.11.2026, Edgar: „playleiste und export für alle 3“)
    testfaelle Karte „Testfälle der KI“ wie auf der Testseite → `/api/meshgenesis/test/<k>/testfaelle/<g>/`
    rechnen    True, wenn ein PSHuman-Netz da ist: Knopf „Genesis rechnen“ (`Fotogenesisgenesisstart`)
    stand      Hinweis, wenn die Kleider des eingestellten Geschlechts älter sind (`Meshgenesistestgeschlechtstand`), sonst None

Fehlt ein Ergebnis, steht statt der Adresse None und unter `hinweise` warum.
    Fotogenesisgenesiszeile.fuer(job)      # dict, bei Exporten None (dort kein Test aus Fotos)
"""
import json
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402

__all__ = ['Fotogenesisgenesiszeile']


class Fotogenesisgenesiszeile:

    @classmethod
    def fuer(cls, job):
        from .fotogenesisgenesisstart import Fotogenesisgenesisstart
        from .meshgenesistest import Meshgenesistest
        from .meshgenesistestanpassung import Meshgenesistestanpassung
        from .meshgenesistestgeschlechtstand import Meshgenesistestgeschlechtstand
        if job.get('art') != 'foto':
            return None
        t = job.get('test')
        ordner = Meshgenesistest.pfad(t) if t else None
        npz = ordner / Meshgenesistestanpassung.ORDNER / 'meshanpassung.npz' if ordner is not None else None
        anpassung = npz is not None and Npztorch.da(npz)
        stand = cls._stand(ordner) if ordner is not None else {}
        # Hat der Test ein Ergebnis, steht die Figur da wie auf der Mesh-Genesis-Testseite, auch während eines neuen Laufs (08.11.2026, Edgar: „laden von genesis mesh … dauert immer noch ewig“:
        # das Feld blieb 50 min leer mit „Test …: laeuft.“) und nach einem Abbruch (11.11.2026, Edgar: „zeige einen fertigen Job an, auch wenn die Prüfung nicht durch ist“:
        # zauberer_mesh_genesis_4 brach erst im letzten Schritt „Prüfung der Kleider“ ab, Figur, Haut und Kleider lagen fertig da, das Feld blieb leer)
        fertig = ordner is not None and (stand.get('status') == 'fertig' or Npztorch.da(ordner / 'ergebnis.npz'))
        form = ordner is not None and any(ordner.glob('form_*/modell.json'))
        ohne = f'Der Mesh-Genesis-Test {t} liegt im Papierkorb, dieser Job hat damit kein Ergebnis.' if cls._im_papierkorb(t) else 'Noch kein Mesh-Genesis-Test zu einem Netz aus diesen Fotos (job.json meshgenesis_test).'
        return {
            'test': t,
            'rechnen': Fotogenesisgenesisstart.eingang(job['ordner'])[0] is not None,
            'meshgenesis': f'/api/meshgenesis/test/{t}/meshanpassung/' if anpassung else None,
            'ergebnis': f'/api/meshgenesis/test/{t}/' if fertig else None,
            'figur': f'/api/meshgenesis/test/{t}/' if form else None,
            'testfaelle': f'/api/meshgenesis/test/{t}/testfaelle/{Meshgenesistest.geschlecht(ordner, {})}/' if fertig else None,
            'stand': Meshgenesistestgeschlechtstand.text(ordner, Meshgenesistest.geschlecht(ordner, {})) if ordner is not None else None,
            'lauf': cls._lauftext(stand),
            'hinweise': {
                'meshgenesis': ohne if ordner is None else f'Einpassung im Test {t} noch nicht gerechnet.',
                # 13.11.2026, Edgar: „es erscheint gar keines, weil es evtl. keines gibt?? dann mach hinweis, dass es fehlt!!“ — vorher nur „Test …: offen.“
                'ergebnis': ohne if ordner is None else cls._lauftext(stand) or (f'Genesis-Ergebnis fehlt: Der Mesh-Genesis-Test {t} hat noch kein Ergebnis '
                                                                                 f'(Stand: {stand.get("status") or "nicht gerechnet"}).'),
            },
        }

    @staticmethod
    def _lauftext(stand):
        """Satz zum laufenden oder abgebrochenen Rechenlauf des Tests (`rechnen/stand.json`), sonst None."""
        if stand.get('status') == 'fehler':
            schritt = next((s for s in stand.get('schritte') or [] if s.get('status') == 'fehler'), {})
            return (f'Der letzte Lauf brach im Schritt „{schritt.get("text") or "?"}“ ab. Gezeigt ist der Stand bis dahin; '
                    'was danach kommt, fehlt oder stammt aus keinem Lauf dieses Tests.')
        if stand.get('status') != 'laeuft':
            return None
        schritte, nr = stand.get('schritte') or [], stand.get('schritt') or 0
        titel = schritte[nr - 1].get('text', '') if 0 < nr <= len(schritte) else ''
        seit = str(stand.get('beginn') or '')[11:16]
        return (f'Der Test wird gerade neu gerechnet{f" (seit {seit})" if seit else ""}, Schritt {nr} von {len(schritte)}{f": {titel}" if titel else ""}. '
                'Gezeigt ist der Stand bis dahin; erst nach dem Lauf neu laden.')

    @staticmethod
    def _stand(ordner):
        try:
            return json.loads((ordner / 'rechnen' / 'stand.json').read_text(encoding='utf-8')) or {}
        except (OSError, ValueError):
            return {}

    @staticmethod
    def _im_papierkorb(kennung):
        from .meshgenesispapierkorb import Meshgenesispapierkorb
        from .meshgenesistest import Meshgenesistest
        return bool(kennung) and bool(Meshgenesistest.KENNUNG.match(str(kennung))) and any(Meshgenesispapierkorb.wurzel().glob(f'_beiseite/*/tests/{kennung}'))
