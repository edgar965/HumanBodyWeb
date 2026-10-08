# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopfnetz — der Runner-Lauf des Schritts „kopf": aus den Kopfausschnitten ein eigenes Kopfnetz (07.10.2026).

Derselbe Runner wie der Schritt „netz" (`_run_mesh.py`, Umgebung `python10_mesh`), mit anderem Eingang: statt der Ganzkörperfotos die drei Kopfausschnitte (`Engine2d3dKleiderkopfausschnitt`,
RGBA, schon freigestellt — Option `freistellen = alpha`, kein zweites BiRefNet und kein Lichtausgleich), das Formmodell und die Flächenzahl aus der Gruppe `kopf`. Alles Übrige entspricht dem
guten Kopflauf vom 27.09.2026 (`…13.23.11`): Octree und Texturgröße aus der Gruppe `mesh`, Textur „ki" (Hunyuans eigene Malerei, bei 2mv aus dem vorderen Ausschnitt), kein Fotobacken (die
Fotoprojektion setzt Ganzkörperfotos voraus), Höhe 170 cm — so normiert der Runner auch dort den Kopf, `Meshfigurkopfnetz` rechnet den Maßstab selbst.

Die Ergebnisse liegen flach in `kopf/` (`mesh.glb`, `icon.png`), die Zwischenstände in `kopf_arbeit/` und `kopf_vorbereitet/`. Auftrag und Fotoliste (`job.bilder`, `job.eingang`, `ergebnis.netz`) bleiben unberührt:
der Schritt trägt sein Ergebnis in `ergebnis.kopf` ein (`Engine2d3dKleiderkopf`).
"""

import logging

from django.conf import settings

from .engine2d3dkleidernetz import Engine2d3dKleidernetz
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .meshicon import Meshicon

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderkopfnetz']


class Engine2d3dKleiderkopfnetz(Engine2d3dKleidernetz):
    #: Was der Kopflauf gegenüber dem Ganzkörperlauf anders einstellt (gelesen am Runner: `_run_mesh.vorbereitung` (alpha), `mesh_hunyuan._hunyuan_form_fertig` (ki), `mesh_export`).
    KOPFLAUF = {'verwendung': 'kopf', 'freistellen': 'alpha', 'licht': 0, 'ausrichten': 'aus', 'bildrand': 0, 'straehnen': 0, 'textur': 'ki', 'fotobacken': 'aus', 'relief': 'aus',
                'kopfanteil': 0, 'mehrbildmodus': 'einzelbild', 'formate': ['glb'], 'fotopruefung': 'aus'}

    def __init__(self, lauf, ausschnitte):
        super().__init__(lauf)
        #: `[{rolle, datei}]` — die Ausschnitte in `kopf/`, `datei` ohne Pfad.
        self.ausschnitte = ausschnitte
        kopf = Engine2d3dKleideroptionen.kopf(self.job.optionen)
        self.optionen.update(self.KOPFLAUF, formmodell=kopf['modell'], modell=kopf['modell'], flaechen=kopf['flaechen'])
        if kopf['modell'] == 'trellis2':
            # TRELLIS.2 hat — anders als Hunyuan3D-2mv — kein eigenes Mehrbild-Modell; ohne das hier sieht die Form
            # nur den vorderen Ausschnitt, Rand und Rückseite sind geraten (Befund 08.10.2026, Edgar 9: Schnittprofile
            # zeigten am Kopfrand bis 16 cm Abweichung, obwohl Augen/Nase/Mund schon gut saßen — die drei ohnehin
            # vorhandenen Ausschnitte (vorne/hinten/rechts, `Engine2d3dKleiderkopf._ausschnitte`) blieben ungenutzt).
            # `Trellismehrbild` ist TRELLIS.2s EIGENER Mehrbild-Sampler (voller Netz-Pfad, PBR-Textur) — fällt unter
            # zwei Ansichten von selbst auf Einzelbild zurück, also unbedenklich auch ohne Vorab-Zählung zu setzen.
            self.optionen['mehrbild'] = 'multidiffusion'
            self.optionen['mehrbild_textur'] = 'multidiffusion'
        #: Was `_abschluss` des Runners meldet — der Schritt trägt es in `ergebnis.kopf` ein.
        self.bericht = None

    def auftragsdatei(self):
        return self.ablage.kopf_arbeit('auftrag.json')

    def beschreibung(self):
        ablage = self.ablage
        ordner = {'vorbereitet': ablage.kopf_vorbereitet(), 'arbeit': ablage.kopf_arbeit(), 'ergebnis': ablage.kopf()}
        for pfad in ordner.values():
            pfad.mkdir(parents=True, exist_ok=True)
        return {
            'kennung': self.job.kennung,
            'name': '%s (Kopf)' % self.job.name,
            'ab': None,
            'optionen': dict(self.optionen),
            'bilder': [{'datei': a['datei'], 'pfad': str(ablage.kopf(a['datei'])), 'rolle': a['rolle'], 'gewicht': 100, 'bereich': None} for a in self.ausschnitte],
            'ordner': {name: str(pfad) for name, pfad in ordner.items()},
            'wurzeln': {'videotobvh': str(settings.VIDEOTOBVH_ROOT)},
        }

    def umgebung(self):
        """Wie beim Netz, Zwischendateien aber in `kopf_arbeit/tmp` (nie System-Temp)."""
        tmp = self.ablage.kopf_arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        return dict(super().umgebung(), TMP=str(tmp), TEMP=str(tmp))

    def _bild(self, roh):
        """Der Befund je Ausschnitt gehört nicht in die Fotoliste des Auftrags (die Ausschnitte stehen dort nicht)."""

    def _abschluss(self):
        glb = self.ablage.netzdatei('kopf')
        if glb is None:
            raise RuntimeError('Der Runner meldet Ergebnis, aber %s fehlt' % self.ablage.kopf(self.ablage.NETZDATEI))
        ergebnis = self._ergebnis
        self.bericht = {
            'datei': glb.name, 'icon': Meshicon.schreiben(glb, self.ablage.kopf()) or None, 'bytes': glb.stat().st_size,
            'flaechen': ergebnis.get('flaechen'), 'punkte': ergebnis.get('punkte'), 'dauer_s': ergebnis.get('dauer_s'),
            'formmodell': ergebnis.get('formmodell'), 'textur_quelle': ergebnis.get('textur_quelle'), 'textur_hinweis': ergebnis.get('textur_hinweis'),
        }
        logger.info('2D3D Kleider %s: Kopfnetz fertig (%s Flächen, %s)', self.job.kennung, ergebnis.get('flaechen'), ergebnis.get('formmodell'))
