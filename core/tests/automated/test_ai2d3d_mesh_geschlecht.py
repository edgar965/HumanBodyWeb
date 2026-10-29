# -*- coding: utf-8 -*-
"""Das Geschlecht der geometrischen Figur (Mesh-Erzeugung, Feld 2 der oberen Zeile der Jobseite) liegt unter der Hose, wo das Foto eine Hose zeigt.

WARUM: Edgar, 29.10.2026 abends, mit einem Bild der Figur (Lauf 2026.10.29.21.00): „erstmal mach einen testcase der das geschlecht in der Mesh erzeugung als falsch erkennt, die
abweichung misst und dann fixt bis es OK ist“. Die Startfigur trug `body_bs_HipGenitalBulge` (Wölbung bis 29 mm); sie hing unter dem Saum der Unterhose vor den Oberschenkeln, im
Bild ein weißer Fleck zwischen den Beinen. Gemessen (`ProjektTemp/_wegwerf/ai2d3d/diag_mesh_pruefungen.py`): 1.jpg 11 sichtbare Punkte der Zone auf Haut, bis 14,5 mm neben der
Hose; 4.jpg 6 Punkte, bis 17,9 mm.

Gemessen je Foto: die Punkte der Anatomie-Zone (`Genesis9.G9meshanatomie.zone`, die Käfigpunkte unter Daz' Anatomie-Stücken — gleiches Netz wie die Figur), sichtbar in diesem
Foto (`Ai2d3dfigurprobe.sichtbar`). Liegt die Mehrheit von ihnen im Foto auf Kleidung (Person ohne Haut, Haar, Bart; Sapiens2), ist die Person dort bekleidet — dann darf kein
sichtbarer Punkt der Zone auf Haut weiter als GRENZE_MM von der Kleidung entfernt liegen (der Saum selbst ist eine Grenze der Segmentierung). Liegt die Mehrheit auf Haut (nackt),
gilt die Prüfung für dieses Foto nicht.

Nur lesen. Ohne training_figur.json wird übersprungen; eine ohne `versatz_px` in der Kamera fällt durch (der Lauf ist vor dem 29.10.2026 abends ausgegeben — neu ausgeben).

    manage.py test core.tests.automated.test_ai2d3d_mesh_geschlecht
"""
from django.conf import settings
from django.test import SimpleTestCase
from scipy import ndimage

from .ai2d3d_figurprobe import Ai2d3dfigurprobe


class Ai2d3dMeshGeschlecht(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    GRENZE_MM = 5.0
    #: Anteil der sichtbaren Zonenpunkte auf Kleidung, ab dem das Foto als bekleidet gilt
    KLEID_MIN = 0.5
    #: Gegenprobe: die Zone so weit nach unten gesenkt (eine hängende Wölbung) muss durchfallen
    SENKEN_MM = 40.0

    def _probe(self):
        p = Ai2d3dfigurprobe(settings.OBJECTS_ROOT, self.JOB)
        if p.figur is None or p.training is None:
            self.skipTest('kein Lauf: training_figur.json oder training.json fehlt')
        self.assertTrue(p.fotos(), 'Lauf %s: keine Kamera mit versatz_px — form_direkt.py … --aus=%s neu ausgeben' % (p.figur.get('lauf'), p.figur.get('lauf')))
        from Genesis9.meshanatomie import G9meshanatomie
        zone = G9meshanatomie.zone()
        self.assertIsNotNone(zone, 'Anatomie-Zone nicht gefunden (Daz Anatomie Mann/Frau in der eigenen Bibliothek)')
        self.assertEqual(len(zone), p.figur['n_punkte'], 'Zone und Figur haben verschiedene Netze')
        return p, zone

    @classmethod
    def messen(cls, p, zone, senken_mm=0.0):
        """[(Foto, sichtbare Zonenpunkte, davon auf Kleidung, auf Haut über GRENZE_MM, größter Abstand mm)] — nur bekleidete Fotos."""
        aus = []
        for nr, f in p.fotos():
            m = p.masken(f['datei'])
            if m is None:
                continue
            x = p.punkte(f)
            x[zone, 1] -= senken_mm / 1000
            uv, z = p.projektion(f, x)
            zs = zone & p.sichtbar(uv, z, f)
            if not zs.any():
                continue
            ix, iy = p.pixel(uv, m['person'].shape)
            kleid = m['person'] & ~m['haut'] & ~m['haar'] & ~m['bart']
            auf_kleid = int((zs & kleid[iy, ix]).sum())
            if auf_kleid < cls.KLEID_MIN * int(zs.sum()):
                continue
            haut = zs & m['haut'][iy, ix]
            d = (ndimage.distance_transform_edt(~kleid) * p.mm_je_px(nr))[iy, ix][haut]
            aus.append((f['datei'], int(zs.sum()), auf_kleid, int((d > cls.GRENZE_MM).sum()), float(d.max()) if len(d) else 0.0))
        return aus

    @staticmethod
    def _text(fotos):
        return ' | '.join('%s: %d sichtbar, %d auf Kleidung, %d auf Haut über der Grenze, max %.1f mm' % e for e in fotos)

    def test_geschlecht_liegt_unter_der_hose(self):
        p, zone = self._probe()
        fotos = self.messen(p, zone)
        self.assertTrue(fotos, 'Lauf %s: in keinem Foto liegt die Zone sichtbar auf Kleidung — nichts gemessen' % p.figur['lauf'])
        self.assertEqual(sum(e[3] for e in fotos), 0, 'Lauf %s, Grenze %.0f mm neben der Kleidung — %s' % (p.figur['lauf'], self.GRENZE_MM, self._text(fotos)))

    def test_gegenprobe_gesenkte_zone_faellt_durch(self):
        p, zone = self._probe()
        fotos = self.messen(p, zone, self.SENKEN_MM)
        self.assertGreater(sum(e[3] for e in fotos), 0, 'Zone %d mm gesenkt, trotzdem nichts auf Haut — %s' % (self.SENKEN_MM, self._text(fotos)))
