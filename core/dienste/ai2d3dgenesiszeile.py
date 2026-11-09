# -*- coding: utf-8 -*-
"""Ai2d3dgenesiszeile — die dritte Zeile der Jobseite jedes Tests aus Fotos (04.11.2026; erst nur PSHuman-Jobs, abends Edgar: „passe sie ans neue Layout an“).

Edgar: „3. Zeile: Genesis - Mesh3d-AI, Genesis - 2d3dai (aus Fotos), Genesis Ergebnis (mes3d-ai)“. Feld 2 ist
das Feld „Genesis-Modell“ der Seite (`daten.test`); hier die beiden Felder aus dem Mesh3D-AI-Test zum
Netz (job.json `mesh3dai_test`; jeder Job steht für sich, 04.11.2026, Edgar: „die jobs sollen immer unabhängig sein“):

    mesh3dai   Genesis – Mesh3D-AI: die Einpassung ohne KI, Zeile 1 der Testseite (`Mesh3daimeshanpassung`)
               → `/api/mesh3dai/test/<k>/meshanpassung/`
    ergebnis   Genesis-Ergebnis (Mesh3D-AI): die Figur des fertigen Tests (Figur aus Zeile 1, Haut, Kleider)
               → `/api/mesh3dai/test/<k>/` (wie `Ai2d3dtestfigur` sie baut)
    figur      Testdaten mit `figur_genesis` (`/api/mesh3dai/test/<k>/`), sobald die Form der Zeile 1 steht
               (`form_<g>/modell.json`: Regler der Einpassung, Versatz als eigene Morphs) — Abspielleiste
               und Export von Feld 1 (04.11.2026, Edgar: „playleiste und export für alle 3“)
    testfaelle Karte „Testfälle der KI“ wie auf der Testseite → `/api/mesh3dai/test/<k>/testfaelle/<g>/`
    rechnen    True, wenn ein PSHuman-Netz da ist: Knopf „Genesis rechnen“ (`Ai2d3dgenesisstart`)
    stand      Hinweis, wenn die Kleider des eingestellten Geschlechts älter sind (`Mesh3daitestgeschlechtstand`), sonst None

Fehlt ein Ergebnis, steht statt der Adresse None und unter `hinweise` warum.
    Ai2d3dgenesiszeile.fuer(job)      # dict, bei Exporten None (dort kein Test aus Fotos)
"""
import json

__all__ = ['Ai2d3dgenesiszeile']


class Ai2d3dgenesiszeile:

    @classmethod
    def fuer(cls, job):
        from .ai2d3dgenesisstart import Ai2d3dgenesisstart
        from .mesh3daitest import Mesh3daitest
        from .mesh3daitestanpassung import Mesh3daitestanpassung
        from .mesh3daitestgeschlechtstand import Mesh3daitestgeschlechtstand
        if job.get('art') != 'foto':
            return None
        t = job.get('test')
        ordner = Mesh3daitest.pfad(t) if t else None
        npz = ordner / Mesh3daitestanpassung.ORDNER / 'meshanpassung.npz' if ordner is not None else None
        anpassung = npz is not None and npz.is_file()
        stand = cls._stand(ordner) if ordner is not None else {}
        # Läuft der Test neu und hat schon ein Ergebnis, steht die Figur trotzdem da wie auf der Mesh3D-AI-Testseite (08.11.2026, Edgar: „laden von genesis mesh … dauert immer noch ewig“:
        # während des Laufs blieb das Feld 50 min leer mit „Test …: laeuft.“)
        fertig = ordner is not None and (stand.get('status') == 'fertig' or (stand.get('status') == 'laeuft' and (ordner / 'ergebnis.npz').is_file()))
        form = ordner is not None and any(ordner.glob('form_*/modell.json'))
        ohne = f'Der Mesh3D-AI-Test {t} liegt im Papierkorb, dieser Job hat damit kein Ergebnis.' if cls._im_papierkorb(t) else 'Noch kein Mesh3D-AI-Test zu einem Netz aus diesen Fotos (job.json mesh3dai_test).'
        return {
            'test': t,
            'rechnen': Ai2d3dgenesisstart.eingang(job['ordner'])[0] is not None,
            'mesh3dai': f'/api/mesh3dai/test/{t}/meshanpassung/' if anpassung else None,
            'ergebnis': f'/api/mesh3dai/test/{t}/' if fertig else None,
            'figur': f'/api/mesh3dai/test/{t}/' if form else None,
            'testfaelle': f'/api/mesh3dai/test/{t}/testfaelle/{Mesh3daitest.geschlecht(ordner, {})}/' if fertig else None,
            'stand': Mesh3daitestgeschlechtstand.text(ordner, Mesh3daitest.geschlecht(ordner, {})) if ordner is not None else None,
            'lauf': cls._lauftext(stand),
            'hinweise': {
                'mesh3dai': ohne if ordner is None else f'Einpassung im Test {t} noch nicht gerechnet.',
                'ergebnis': ohne if ordner is None else cls._lauftext(stand) or f'Test {t}: {stand.get("status") or "offen"}.',
            },
        }

    @staticmethod
    def _lauftext(stand):
        """Satz zum laufenden Rechenlauf des Tests (`rechnen/stand.json`), sonst None."""
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
        from .mesh3daipapierkorb import Mesh3daipapierkorb
        from .mesh3daitest import Mesh3daitest
        return bool(kennung) and bool(Mesh3daitest.KENNUNG.match(str(kennung))) and any(Mesh3daipapierkorb.wurzel().glob(f'_beiseite/*/tests/{kennung}'))
