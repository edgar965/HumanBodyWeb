# -*- coding: utf-8 -*-
"""Ai2d3dseitendaten — was die Jobseite `/2d-3d-AI/<job>/` im Browser braucht (24.10.2026), als JSON in der Seite (`json_script`).

    {id, name, art, wahrheit, hinweis, fotos: [{nr, name, winkel, adresse}], netze: [{art, name, mb, adresse}], smplx: {art, name, mb, adresse} | None, pshuman: (ebenso) | None, genesis, test,
     kamera}

`genesis` (nur Exporte mit Mesh3D-AI-Paar): wo der Browser Probe und Figuren holt — dieselben Endpunkte wie die Mesh3D-AI-Jobseite (`/api/mesh3dai/<paar>/proben/`, `…/genesis/1/`), gebaut wird
mit `Mesh3daigenesisfigur` (Code der Charakter-Seite). `kamera`: die Regel, nach der die Charakter-Seite die vier Fotos aufnimmt (`Modellansichten`: 20°, Hülle × 1,08, 1536 × 2048, Grund 25/26/46)
— nur bei Exporten; bei echten Fotos ist die Kamera unbekannt (`None`).
"""

__all__ = ['Ai2d3dseitendaten']


class Ai2d3dseitendaten:
    #: `static/viewer/charakter/modellansichten.js` (FOV, RAND, BREITE, HOEHE) und der Grund der Szene in Edgars Exporten (`_bild3d/*/bilder/bilder.json` → `grund_rgb`).
    KAMERA_EXPORT = {'fov': 20, 'rand': 1.08, 'breite': 1536, 'hoehe': 2048, 'grund': [25, 26, 46]}

    #: Netzarten, die nicht ins Feld „Netz“ gehen, sondern als eigenes Feld in jede Zeile (`smplx`, `ai2d3dsmplx.js`): der Startkörper der Netzformung. Genesis seit 07.11.2026, SMPL-X in alten Jobs und bei UP2You
    STARTKOERPER = ('pshuman_start', 'pshuman_smplx')
    #: PSHumans Endnetz — zusätzlich als eigenes Feld in jeder Zeile (`pshuman`,
    #: `_ai2d3d_pshumanfeld.html`); bleibt auch im Feld „Netz“
    PSHUMAN = 'pshuman'

    @classmethod
    def fuer(cls, job):
        k = job['id']
        paar = job['paar']
        netze = [{'art': n['art'], 'name': n['name'], 'mb': round(n['bytes'] / 1e6, 1), 'adresse': '/api/2d3dai/%s/netz/%s/' % (k, n['art'])} for n in job['netze']]
        return {
            'id': k, 'name': job['name'], 'art': job['art'], 'wahrheit': job['wahrheit'], 'hinweis': job['hinweis'], 'figur': job['figur'],
            'fotos': [{'nr': i, 'name': f['name'], 'winkel': f['winkel'], 'adresse': '/api/2d3dai/%s/foto/%d/' % (k, i), 'frei': bool(f.get('frei'))} for i, f in enumerate(job['fotos'])],
            'netze': [n for n in netze if n['art'] not in cls.STARTKOERPER],
            # 03.11.2026: PSHumans Startkörper, seit 04.11. Feld 2 der Zeile mit den Genesis-Feldern — oder None
            'smplx': next((n for art in cls.STARTKOERPER for n in netze if n['art'] == art), None),
            # 04.11.2026, Edgar: „das ergebnis sollte doch auch ein Mesh sein, das ich im 3d View rotieren
            # kann?“ — „pshuman als zusätzliches Feld / View“: PSHumans Netz — oder None
            'pshuman': next((n for n in netze if n['art'] == cls.PSHUMAN), None),
            # 04.11.2026: dritte Zeile, drei Wege PSHuman-Netz → Genesis (`Ai2d3dgenesiszeile`) — oder None
            'genesiszeile': cls._genesiszeile(job),
            'genesis': {'job': paar['kennung'], 'name': paar['name'], 'seite': '/mesh-3D-AI/%s/' % paar['kennung'],
                        'proben': '/api/mesh3dai/%s/proben/' % paar['kennung']} if paar else None,
            # `adresse` (24.10.2026, Edgar: „Ich sehe den job nicht mit den bildern“): ohne Paar baut Feld 3 die Ausgabe dieses Tests (`Ai2d3dtestfigur`). Hat der Job eine eigene Figur
            # (`<Job>/figur/`, 25.10.2026 „das ist doch eine andere Pipeline“), kommt sie von `/api/2d3dai/<job>/figur/` (`eigen`), sonst bei einem Export die Messlatte A des Mesh3D-AI-Tests.
            # Ein Foto-Job zeigt in Feld „Genesis – 2d3dai (aus Fotos)“ NUR die eigene Figur: der Rückfall zeigte dort die Mesh3D-AI-Figur unter falschem Titel (04.11.2026, Edgar: „warum ist diese Fotokette denn gerechnet worden für den Edgar 1 job??“).
            'test': cls._test(job),
            'kamera': cls.KAMERA_EXPORT if job['art'] == 'export' else None,
            # Feld „Körpergröße“ oben auf der Testseite (`Ai2d3dkoerpergroesse`, 24.10.2026); Meter oder None
            'koerpergroesse_m': job.get('koerpergroesse_m'),
            # 27.10.2026: die gerechnete Figur der Kopf-KI (`<Job>/abnahme/training_figur.json`, `Trainingfigur`) — dann Feld 2 der oberen Zeile in 3D, das Genesis-Modell in Feld 3
            'trainingfigur': '/api/2d3dai/%s/abnahme/trainingfigur/' % k if cls._trainingfigur(job) else None,
        }

    @staticmethod
    def _genesiszeile(job):
        from .ai2d3dgenesiszeile import Ai2d3dgenesiszeile
        return Ai2d3dgenesiszeile.fuer(job)

    @staticmethod
    def _trainingfigur(job):
        from pathlib import Path
        return job.get('art') == 'foto' and bool(job.get('ordner')) and (Path(job['ordner']) / 'abnahme' / 'training_figur.json').is_file()

    @staticmethod
    def _test(job):
        from .ai2d3dfigur import Ai2d3dfigur
        eigen = Ai2d3dfigur.adresse(job)
        if eigen:
            return {'kennung': job['id'], 'eigen': True, 'seite': None, 'adresse': eigen}
        t = job['test']
        return {'kennung': t, 'eigen': False, 'seite': '/mesh-3D-AI/test/%s/' % t, 'adresse': '/api/mesh3dai/test/%s/' % t} if t and job['art'] != 'foto' else None
