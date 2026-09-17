# -*- coding: utf-8 -*-
"""`Pfadwurzeln` — welche Verzeichnisse ein Endpunkt beschreiben darf.

Ein Waechter, der das ganze Arbeitsverzeichnis freigibt, ist keiner: Der
erste Wurf hatte `TOOLS_ROOT` in der Liste, und damit gingen
`ui/settings.py`, `.git/` und die `.npy`-Morphdaten durch. Genau das
nagelt dieser Test fest.
"""

from django.test import TestCase

from core.daten.pfadwurzeln import Pfadwurzeln


class PfadwurzelnTest(TestCase):
    """Welche Verzeichnisse ein Endpunkt beschreiben darf.

    `TestCase` und nicht `SimpleTestCase`: `Pfadwurzeln.aus_einstellungen`
    liest `AppSettings` aus der Datenbank. In einem `SimpleTestCase` wirft der
    Zugriff, die Methode faengt ihn ab und liefert eine LEERE Liste — der Test
    liefe dann gegen ein abgewuergtes Ergebnis und saehe grueneres Land, als
    da ist.
    """

    def test_tools_root_ist_keine_wurzel(self):
        """DER BEFUND VOM 12.08.2026, festgenagelt.

        Der erste Wurf hatte `TOOLS_ROOT` in der Liste — damit gingen
        `A:\\3DTools\\evil.json`, `ui/settings.py`, `.git/` und die
        `.npy`-Morphdaten durch. Ein Wächter, der das ganze
        Arbeitsverzeichnis freigibt, ist keiner.
        """
        from django.conf import settings
        werkzeuge = str(settings.TOOLS_ROOT)
        for name in ('studio_projekte', 'ausgabe', 'videos'):
            wurzeln = [str(w) for w in getattr(Pfadwurzeln, name)()]
            self.assertNotIn(werkzeuge, wurzeln,
                             '%s() gibt TOOLS_ROOT frei' % name)

    def test_medien_sind_ueberall_dabei(self):
        medien = str(Pfadwurzeln.medien())
        for name in ('studio_projekte', 'ausgabe', 'videos'):
            wurzeln = [str(w) for w in getattr(Pfadwurzeln, name)()]
            self.assertIn(medien, wurzeln, '%s() ohne MEDIA_ROOT' % name)

    def test_bvh_nimmt_die_uebergebene_wurzel_mit(self):
        from pathlib import Path
        eigene = Path('A:/beispiel/bvh')
        self.assertIn(eigene, Pfadwurzeln.bvh(eigene))

    def test_videos_nehmen_den_videoordner_der_uploadseite_an(self):
        """15.09.2026, Edgar: „Start fehlgeschlagen: 403 Forbidden bei
        /api/job/create-from-file/". Die Uploadseite listet `3DObjects/Video`
        (`Videoauswahl.sammeln`), `videos()` kannte den Ordner nicht — seit
        dem 24.08. war jedes Video von dort abgelehnt. Was die Oberflaeche
        anbietet, muss die Pruefung annehmen. Und ganz `3DObjects/` ist frei
        (Edgar: „diese Ordner sollen nicht gesperrt sein")."""
        from django.conf import settings
        from core.safe_paths import SafePath
        from core.dienste import videoauswahl
        ordner = Pfadwurzeln.videoordner()
        self.assertEqual(ordner, settings.TOOLS_ROOT / '3DObjects' / 'Video')
        self.assertIn(settings.TOOLS_ROOT / '3DObjects', Pfadwurzeln.videos())
        SafePath.fuer_videos().pruefe(str(Pfadwurzeln.objekte() / 'Recherche' / 'x.mp4'))
        self.assertIn('Pfadwurzeln.videoordner()',
                      open(videoauswahl.__file__, encoding='utf-8').read())
        geprueft = SafePath.fuer_videos().pruefe(str(ordner / '005 DanceLang.mp4'))
        self.assertEqual(geprueft.name, '005 DanceLang.mp4')

