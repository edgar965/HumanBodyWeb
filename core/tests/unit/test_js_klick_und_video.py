# -*- coding: utf-8 -*-
"""Drei Fehler vom 08.10.2026 (Edgar, abends), am Quelltext — die Module hängen an `three`, das der Node-Harness nicht löst.

1. **Klick aufs T-Shirt trifft die Ruhehaltung** (`gemeinsam/raycastbeschleunigung.js`): Der Suchbaum von three-mesh-bvh
   steht über den Punkten der Ruhehaltung und kennt keine Häutung. Gemessen am Modell „Edgar" (Spine und Oberarme gedreht):
   `acceleratedRaycast` 121 Treffer bei z 0,074 wie in Ruhe, `Mesh.raycast` 77 Treffer bei z 0,235. In der Tanzhaltung traf
   der Klick auf den Ärmel nichts (Gegenprobe im Chrome: alter Raycast → keine Auswahl, korrekter → G9 Base Shirt gewählt);
   ein Klick, der ein ANDERES Stück traf, legte das Farbfeld des gewählten Stücks auf die Hose.
2. **Video ohne Bewegung** (`charakter/videoaufnahme.js`): Eine pausierte Aktion rechnet mit Zeitmaß 0, `mixer.setTime(t)` stellt
   bei jedem t dieselbe Haltung (Quaternion l_upperarm bei t = 1, 2, 3 s identisch; mit `paused = false` drei verschiedene).
   `Edgar.mp4` (DanceLang, 120 Bilder): mittlerer Unterschied zum ersten Bild 0,05 von 255.
3. **Ganzer Pfad im Feld „Ablage"** (`charakter/figurvideo.js`): `A:\\Videos\\Edgar.mp4` wird in Ordner und Datei geteilt —
   sonst legte der Server `Edgar.mp4` als Ordner an.

Sabotage-Gegenprobe: in 1. `mesh.isSkinnedMesh ? … : acceleratedRaycast` durch `acceleratedRaycast` ersetzen → Fall 1 rot;
in 2. `aktion.paused = false` streichen → Fall 2 rot; in 3. das `.mp4` aus dem Muster nehmen → Fall 3 rot (`A:\\Videos\\v1.2` würde zur Datei).
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class KlickUndVideoJsTest(SimpleTestCase):
    databases = set()

    def test_1_gehaeutete_netze_nehmen_den_suchbaum_nur_in_ruhe(self):
        text = quelltext('gemeinsam', 'raycastbeschleunigung.js')
        self.assertIn('mesh.raycast = mesh.isSkinnedMesh ? Raycastbeschleunigung._gehaeutet : acceleratedRaycast;', text)
        self.assertIn('Raycastbeschleunigung.ruhend(this) ? acceleratedRaycast : THREE.Mesh.prototype.raycast', text)
        self.assertIn('skelett.update();', text, 'die Knochenmatrizen müssen zum Stand der Knochen passen')
        self.assertIn('(i % 16) % 5 === 0 ? 1 : 0', text, 'Ruhe heißt: jede Knochenmatrix ist die Einheitsmatrix')

    def test_2_aufnahme_gibt_eine_pausierte_aktion_frei(self):
        text = quelltext('charakter', 'videoaufnahme.js')
        self.assertIn('const vorher = { pausiert: aktion.paused, tempo: state.mixer.timeScale, zeit: aktion.time };', text)
        self.assertIn('aktion.paused = false;', text)
        self.assertIn('state.mixer.timeScale = 1;', text, 'setTime rechnet mit dem Tempo-Regler')
        self.assertIn('aktion.paused = vorher.pausiert;', text, 'nach der Aufnahme steht die Aktion wieder, wie sie war')
        self.assertIn('aktion.time = vorher.zeit;', text, 'und an der Stelle, an der der Nutzer sie hatte')
        self.assertLess(text.index('aktion.paused = false;'), text.index('await this._aufnehmen('))
        self.assertGreater(text.index('aktion.paused = vorher.pausiert;'), text.index('} finally {'))

    def test_2b_video_erzeugen_nimmt_die_ganze_animation_auf(self):
        """Edgar, 08.10.2026: „der button Video erzeugen soll das ganze Video für diese animation erzeugen, egal ob sie
        läuft oder nicht" — nicht ab der Abspielstelle und nicht nur `Länge` Sekunden."""
        text = quelltext('charakter', 'videoaufnahme.js')
        self.assertIn('const anfang = Videoaufnahme.VORLAUF / fps;', text)
        self.assertIn('const ab = modus === Videoaufnahme.SICHTBAR ? Math.max(abspielstelle, anfang) : anfang;', text,
                      'GANZ beginnt von vorn, nicht an der Abspielstelle')
        self.assertIn('const dauer = Math.max(clip.duration - von, 0);', text)
        self.assertNotIn('figurvideo-sekunden', text)
        video = quelltext('charakter', 'figurvideo.js')
        self.assertNotIn('figurvideo-sekunden', video, 'der Regler „Länge" ist weg')
        self.assertIn('ab_sekunden: Videoaufnahme.VORLAUF / Videoaufnahme.FPS,', video, 'der Server-Weg ebenso')
        vorlage = (Path(settings.BASE_DIR) / 'templates' / '_figurvideo.html').read_text(encoding='utf-8')
        self.assertNotIn('figurvideo-sekunden', vorlage)

    def test_2c_zwei_knoepfe_sichtbar_und_ganz(self):
        """Edgar, 08.10.2026: „mach einen zweiten Button: Video erzeugen default, der das ganze Video der Animation
        erzeugt. Der Video erzeugen soll mir das erzeugen, was im Browser läuft, mit der Kamera Einstellung die ich
        manuell mache" — „Video erzeugen" (SICHTBAR) ab der Abspielstelle ohne Kamerafolge, „default" (GANZ) alles."""
        aufnahme = quelltext('charakter', 'videoaufnahme.js')
        self.assertIn('const folge = modus === Videoaufnahme.SICHTBAR ? null : this._kamerafolge(inst);', aufnahme,
                      'SICHTBAR führt die Kamera nicht nach')
        self.assertIn('await this._aufnehmen(inst, mm, modus, vorher.zeit)', aufnahme)
        video = quelltext('charakter', 'figurvideo.js')
        self.assertIn('this.aufnahme.starten(Videoaufnahme.SICHTBAR);', video, '„Video erzeugen" nimmt immer die Szene auf')
        self.assertIn("document.getElementById('figurvideo-start-ganz')", video)
        self.assertIn('else this.aufnahme.starten(Videoaufnahme.GANZ);', video)
        vorlage = (Path(settings.BASE_DIR) / 'templates' / '_figurvideo.html').read_text(encoding='utf-8')
        self.assertIn('id="figurvideo-start-ganz"', vorlage)
        self.assertIn('Video erzeugen default</button>', vorlage)
        anzeige = quelltext('charakter', 'figurvideo_anzeige.js')
        self.assertIn("['figurvideo-start', 'figurvideo-start-ganz']", anzeige, 'beide Knöpfe werden zusammen gesperrt')

    def test_2d_abbrechen_beendet_aufnahme_und_server_job(self):
        """Edgar, 08.10.2026: „mach einen Button Abbrechen für die Video Erzeugung und brich den job ab"."""
        aufnahme = quelltext('charakter', 'videoaufnahme.js')
        self.assertIn('if (this._abbruch) return null;', aufnahme, 'die Aufnahme hört vor dem nächsten Bild auf')
        self.assertIn('if (this._abbruch) return 0;', aufnahme, 'auch die Kalibrierung')
        self.assertIn('if (!bilder) { this.anzeige.abgebrochen(); return; }', aufnahme, 'nichts geht an den Server')
        self.assertIn('if (this.laeuft && !this._kodiert) this._abbruch = true;', aufnahme)
        self.assertLess(aufnahme.index('this.anzeige.abbruchFrei(false);'), aufnahme.index('await this._kodieren('),
                        'beim Senden ist „Abbrechen" gesperrt — die Anfrage läuft zu Ende')
        video = quelltext('charakter', 'figurvideo.js')
        self.assertIn("/api/animation/video/${kennung}/abbrechen/", video)
        self.assertIn("document.getElementById('figurvideo-abbrechen')", video)
        self.assertLess(video.index('const antwort = await Serverabruf.senden('), video.index('this.aufraeumen();\n            Anzeige.abgebrochen();'),
                        'die Abfrage hört erst nach dem geglückten Abbruch auf')
        vorlage = (Path(settings.BASE_DIR) / 'templates' / '_figurvideo.html').read_text(encoding='utf-8')
        self.assertRegex(vorlage, r'<button id="figurvideo-abbrechen"[^>]* disabled')
        urls = (Path(settings.BASE_DIR) / 'core' / 'urls.py').read_text(encoding='utf-8')
        self.assertIn("path('api/animation/video/<str:kennung>/abbrechen/', Figurvideoendpunkte.abbrechen", urls)

    def test_3_ganzer_pfad_wird_in_ordner_und_datei_geteilt(self):
        text = quelltext('charakter', 'figurvideo.js')
        muster = re.search(r'const treffer = /(.+)/i\.exec\(roh\);', text)
        self.assertIsNotNone(muster, 'pfadTeilen nicht gefunden')
        regel = re.compile(muster.group(1), re.IGNORECASE)
        treffer = regel.match(r'A:\3DTools\HumanBodyWeb\media\figurvideos\Edgar.mp4')
        self.assertEqual(treffer.groups(), (r'A:\3DTools\HumanBodyWeb\media\figurvideos', 'Edgar.mp4'))
        self.assertEqual(regel.match('A:/Videos/EDGAR.MP4').groups(), ('A:/Videos', 'EDGAR.MP4'))
        self.assertIsNone(regel.match(r'A:\Videos\v1.2'), 'ein Ordner mit Punkt bleibt ein Ordner')
        self.assertIsNone(regel.match(r'A:\Videos'))
        self.assertIn("addEventListener('change', () => this.ablageAufteilen())", text)
        self.assertIn('dateiname: document.getElementById(\'figurvideo-datei\')?.value.trim() || geteilt.datei', text)
