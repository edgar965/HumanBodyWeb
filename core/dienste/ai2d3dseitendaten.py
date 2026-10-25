# -*- coding: utf-8 -*-
"""Ai2d3dseitendaten — was die Jobseite `/2d-3d-AI/<job>/` im Browser braucht (24.10.2026), als JSON in der Seite (`json_script`).

    {id, name, art, wahrheit, hinweis, fotos: [{nr, name, winkel, adresse}], netze: [{art, name, mb, adresse}], genesis, test, kamera}

`genesis` (nur Exporte mit Mesh3D-AI-Paar): wo der Browser Probe und Figuren holt — dieselben Endpunkte wie die Mesh3D-AI-Jobseite (`/api/mesh3dai/<paar>/proben/`, `…/genesis/1/`), gebaut wird
mit `Mesh3daigenesisfigur` (Code der Charakter-Seite). `kamera`: die Regel, nach der die Charakter-Seite die vier Fotos aufnimmt (`Modellansichten`: 20°, Hülle × 1,08, 1536 × 2048, Grund 25/26/46)
— nur bei Exporten; bei echten Fotos ist die Kamera unbekannt (`None`).
"""

__all__ = ['Ai2d3dseitendaten']


class Ai2d3dseitendaten:
    #: `static/viewer/charakter/modellansichten.js` (FOV, RAND, BREITE, HOEHE) und der Grund der Szene in Edgars Exporten (`_bild3d/*/bilder/bilder.json` → `grund_rgb`).
    KAMERA_EXPORT = {'fov': 20, 'rand': 1.08, 'breite': 1536, 'hoehe': 2048, 'grund': [25, 26, 46]}

    @classmethod
    def fuer(cls, job):
        k = job['id']
        paar = job['paar']
        return {
            'id': k, 'name': job['name'], 'art': job['art'], 'wahrheit': job['wahrheit'], 'hinweis': job['hinweis'], 'figur': job['figur'],
            'fotos': [{'nr': i, 'name': f['name'], 'winkel': f['winkel'], 'adresse': '/api/2d3dai/%s/foto/%d/' % (k, i), 'frei': bool(f.get('frei'))} for i, f in enumerate(job['fotos'])],
            'netze': [{'art': n['art'], 'name': n['name'], 'mb': round(n['bytes'] / 1e6, 1), 'adresse': '/api/2d3dai/%s/netz/%s/' % (k, n['art'])} for n in job['netze']],
            'genesis': {'job': paar['kennung'], 'name': paar['name'], 'seite': '/mesh-3D-AI/%s/' % paar['kennung'],
                        'proben': '/api/mesh3dai/%s/proben/' % paar['kennung']} if paar else None,
            # `adresse` (24.10.2026, Edgar: „Ich sehe den job nicht mit den bildern“): ohne Paar baut Feld 3 die Ausgabe dieses Tests (`Ai2d3dtestfigur`). Hat der Job eine eigene Figur
            # (`<Job>/figur/`, 25.10.2026 „das ist doch eine andere Pipeline“), kommt sie von `/api/2d3dai/<job>/figur/` (`eigen`), sonst die Messlatte A des Mesh3D-AI-Tests.
            'test': cls._test(job),
            'kamera': cls.KAMERA_EXPORT if job['art'] == 'export' else None,
            # Feld „Körpergröße“ oben auf der Testseite (`Ai2d3dkoerpergroesse`, 24.10.2026); Meter oder None
            'koerpergroesse_m': job.get('koerpergroesse_m'),
        }

    @staticmethod
    def _test(job):
        from .ai2d3dfigur import Ai2d3dfigur
        eigen = Ai2d3dfigur.adresse(job)
        if eigen:
            return {'kennung': job['id'], 'eigen': True, 'seite': None, 'adresse': eigen}
        t = job['test']
        return {'kennung': t, 'eigen': False, 'seite': '/mesh-3D-AI/test/%s/' % t, 'adresse': '/api/mesh3dai/test/%s/' % t} if t else None
