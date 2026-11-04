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

Fehlt ein Ergebnis, steht statt der Adresse None und unter `hinweise` warum.
    Ai2d3dgenesiszeile.fuer(job)      # dict, bei Exporten None (dort kein Test aus Fotos)
"""
import json

__all__ = ['Ai2d3dgenesiszeile']


class Ai2d3dgenesiszeile:

    @classmethod
    def fuer(cls, job):
        from .mesh3daitest import Mesh3daitest
        from .mesh3daitestanpassung import Mesh3daitestanpassung
        if job.get('art') != 'foto':
            return None
        t = job.get('test')
        ordner = Mesh3daitest.pfad(t) if t else None
        npz = ordner / Mesh3daitestanpassung.ORDNER / 'meshanpassung.npz' if ordner is not None else None
        anpassung = npz is not None and npz.is_file()
        fertig = ordner is not None and cls._status(ordner) == 'fertig'
        form = ordner is not None and any(ordner.glob('form_*/modell.json'))
        ohne = 'Noch kein Mesh3D-AI-Test zu einem Netz aus diesen Fotos (job.json mesh3dai_test).'
        return {
            'test': t,
            'mesh3dai': f'/api/mesh3dai/test/{t}/meshanpassung/' if anpassung else None,
            'ergebnis': f'/api/mesh3dai/test/{t}/' if fertig else None,
            'figur': f'/api/mesh3dai/test/{t}/' if form else None,
            'hinweise': {
                'mesh3dai': ohne if ordner is None else f'Einpassung im Test {t} noch nicht gerechnet.',
                'ergebnis': ohne if ordner is None else f'Test {t}: {cls._status(ordner) or "offen"}.',
            },
        }

    @staticmethod
    def _status(ordner):
        try:
            return json.loads((ordner / 'rechnen' / 'stand.json').read_text(encoding='utf-8')).get('status')
        except (OSError, ValueError):
            return None
