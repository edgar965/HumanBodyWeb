# -*- coding: utf-8 -*-
u"""Schwebehilfe der Zeitleiste: jede Spur- und Clipart hat einen Text, und
was der Text als Menüpunkt oder Taste nennt, gibt es im Studio wirklich.

WARUM (11.09.2026, Edgar: „hover texte in der Timeline mit hilfe was ich tun
muss"): Eine Hilfe, die einen Menüpunkt nennt, den es nicht mehr gibt, ist
schlimmer als keine — man sucht ihn. Der Test hält die Texte an die Vorlage
und die Module, in denen die genannten Dinge stehen.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STUDIO = Jsmodul.VIEWER / 'bvh_studio'
MODUL = Jsmodul('bvh_studio', 'hilfetexte_zeitleiste.js')

SKRIPT = """
const { HILFE_ZEITLEISTE } = await import(MODUL);
console.log(JSON.stringify(HILFE_ZEITLEISTE));
"""

SPURARTEN = ('bvh', 'model', 'camera', 'light', 'audio', 'scene_object', 'floor')
CLIPARTEN = ('bvh', 'model', 'camera_kf', 'light_kf', 'audio', 'object_clip')

#: Was ein Text nennt → wo es im Studio steht: (Wort im Text, Datei, Suchtext).
BELEGE = {
    'camera': [('Kameraposition', 'zeitleiste_spurmenue.js', "'Kameraposition'"),
               ('<b>K</b>', 'playback.js', "e.code === 'KeyK'"),
               ('„Aktiv"', 'properties.js', 'Aktiv:')],
    'light': [('Lichteigenschaft', 'menue_licht.js', "'Lichteigenschaft (einzel)'"),
              ('<b>Alt+Klick</b>', 'lichtsetzen.js', 'e.altKey'),
              ('<b>K</b>', 'playback.js', "fn.addLightKeyframe(state.selectedTrackIdx)")],
    'audio': [('Audio-Datei wählen', 'zeitleiste_spurmenue.js', "'Audio-Datei wählen...'")],
    'scene_object': [('3D-Datei wählen', 'zeitleiste_spurmenue.js', "'3D-Datei wählen...'"),
                     ('<b>Alt+Klick</b>', 'lichtsetzen.js', "spur.type === 'scene_object'")],
    'model': [('„Modell wählen"', '../../../templates/bvh_studio.html', 'Modell w&auml;hlen:'),
              ('verknüpft', 'zeitleiste_kontextmenue.js', '_verknuepfungszeile')],
    'bvh': [('<b>Doppelklick</b>', 'bibliotheksbaum.js', "'dblclick'"),
            ('<b>Ziehen</b>', 'zeitleiste_spurkopf.js', "'drop'")],
    'clip_bvh': [('<b>S</b>', '../../../templates/bvh_studio.html', 'Split an Playhead (S)'),
                 ('Duplizieren', '../../../templates/bvh_studio.html', 'Duplizieren'),
                 ('Smooth', '../../../templates/bvh_studio.html', 'Smooth'),
                 ('Bodenniveau', '../../../templates/bvh_studio.html', 'Bodenniveau'),
                 ('Trim', 'zeitleiste_ziehen.js', "'trim-left'")],
    'clip_camera_kf': [('„Aktuelle Ansicht übernehmen"', 'eigenschaften/klip_schluesselbilder.js',
                        'Aktuelle Ansicht übernehmen')],
    'lineal': [('<b>Leertaste</b>', 'playback.js', "e.code === 'Space'"),
               ('<b>Alt+Ziehen</b>', 'zeitleiste_ziehen.js', "e.button === 0 && e.altKey")],
}


class HilfetexteZeitleisteTest(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.texte = MODUL.laufen(SKRIPT)

    def test_jede_spur_und_clipart_hat_einen_text(self):
        fehlend = [a for a in SPURARTEN if a not in self.texte]
        fehlend += ['clip_' + a for a in CLIPARTEN if 'clip_' + a not in self.texte]
        self.assertEqual(fehlend, [])
        for schluessel, eintrag in self.texte.items():
            self.assertTrue(eintrag.get('titel') and eintrag.get('text'), schluessel)

    def test_genannte_dinge_gibt_es(self):
        fehlend = []
        for schluessel, belege in BELEGE.items():
            self.assertIn(schluessel, self.texte)
            text = self.texte[schluessel]['text']
            for wort, datei, suchtext in belege:
                if wort not in text:
                    fehlend.append('%s: Text nennt „%s" nicht' % (schluessel, wort))
                inhalt = (STUDIO / datei).read_text(encoding='utf-8')
                if suchtext not in inhalt:
                    fehlend.append('%s: „%s" nicht in %s' % (schluessel, suchtext, datei))
        self.assertEqual(fehlend, [], '\n'.join(fehlend))

    def test_keine_ae_oe_ue_schreibweise(self):
        """User-sichtbare Texte tragen echte Umlaute."""
        for schluessel, eintrag in self.texte.items():
            for wort in ('waehlen', 'loescht', 'fuer', 'ueber', 'Staerke', 'Laenge'):
                self.assertNotIn(wort, eintrag['text'], schluessel)
