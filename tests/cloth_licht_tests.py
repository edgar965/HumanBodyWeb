# -*- coding: utf-8 -*-
"""Cloth Export: Lichter und Farben durch alle drei Motoren

Aus `cloth_engine_tests.py` herausgeloest (02.09.2026): Die Datei hatte
324 Zeilen — Befund `dateigroesse` — und zwei ihrer Faelle waren bis auf
den Modulnamen wortgleich (`doppelcode`, 10 Zeilen). Die Doppelung
steht jetzt einmal als `_lichterprobe`.

WARUM BEIDE HAELFTEN GEPRUEFT WERDEN
====================================
Gegenprobe vom 01.09.2026: `bake.get('lights')` steht im Renderweg auch
dann noch, wenn der Leser das Feld gar nicht mehr aus der Datei holt.
Die Sabotage „Feld `lights_json` entfernt" blieb damit unerkannt — die
Pruefung meldete gruen fuer einen Weg, der garantiert ohne Lichter
rendert. Deshalb wird das Lesen (`bakedatei`) UND das Benutzen
(Renderweg) einzeln geprueft.

DER DRITTE MOTOR FEHLTE
=======================
Fuer `warp_blender` und `warp_only` gab es je eine Farbpruefung; EEVEE
blieb ungeprueft und hat jede Kleidung magenta gerendert, waehrend
dieselbe Szene in den beiden anderen Motoren die gewaehlte Farbe zeigte.
Die Farben lagen in der Datei — `load_scene` las sie nur nicht mit.
"""
from .base import TestCategory
# siehe `cloth_engine_tests`: der Aufruf setzt `sys.path` fuer `collision.*`.
from ._cloth_basis import Clothbasis
import inspect

Clothbasis.pfad_sichern()


class ClothLichtTests(TestCategory):
    name = 'Cloth Export: Lichter und Farben'
    description = (
        'Lichter durch alle drei Motoren, Segment- und Koerperfarbe')

    #: Woran man erkennt, dass die Farbe aus dem Bake kommt.
    SEGMENTFARBE = ("seg.get('color')", "seg['color']", 'segment_color')

    @staticmethod
    def test_blender_eevee_uses_payload_lights():
        import collision.blender_script as bs
        src = (inspect.getsource(bs.main)
               + inspect.getsource(bs.Blenderszene))
        return (
            'setup_lights_from_payload' in src,
            'OK' if 'setup_lights_from_payload' in src else 'Lichter-Setup fehlt')

    #: Aus der `.npz` gelesen wird das Feld `lights_json` — das macht
    #: seit dem 01.09.2026 `Bakedatei` fuer alle Wege.
    LICHTFELD = 'lights_json'

    #: Im Renderweg muss die gelesene Liste dann auch ANKOMMEN.
    LICHTMARKEN = ("scene['lights']", "scene_data['lights']",
                   "bake['lights']", "bake.get('lights'",
                   "szene['lights']")

    @staticmethod
    def _lichter_kommen_an(renderweg):
        u"""(gelesen, benutzt) — beide Haelften einzeln.

        NUR EINE HAELFTE ZU PRUEFEN REICHT NICHT (Gegenprobe vom
        01.09.2026): `bake.get('lights')` steht im Renderweg auch dann
        noch, wenn der Leser das Feld gar nicht mehr aus der Datei
        holt. Die Sabotage „Feld `lights_json` entfernt" blieb damit
        unerkannt — die Pruefung meldete gruen fuer einen Weg, der
        garantiert ohne Lichter rendert.
        """
        import collision.bakedatei as bd
        gelesen = ClothLichtTests.LICHTFELD in inspect.getsource(bd)
        quelle = inspect.getsource(renderweg)
        benutzt = any(m in quelle for m in ClothLichtTests.LICHTMARKEN)
        return gelesen, benutzt

    @staticmethod
    def _urteil(gelesen, benutzt):
        """Der Meldungstext — er stand fuer beide Renderwege wortgleich da.

        Das URTEIL bleibt im Testrumpf. Ein `return helfer(...)` sagt
        weder dem Leser noch dem Werkzeug `szenarien`, dass hier
        ueberhaupt etwas behauptet wird — es meldete beide Faelle als
        „Pruefung ohne Zusicherung".
        """
        if gelesen and benutzt:
            return 'OK'
        return ('Bakedatei liest `lights_json` nicht mehr' if not gelesen
                else 'Renderweg benutzt die Lichter nicht')

    @staticmethod
    def test_warp_blender_uses_payload_lights():
        """Gelesen wird `bakedatei` UND der Renderweg."""
        import collision.blender_render_from_bake as m
        gelesen, benutzt = ClothLichtTests._lichter_kommen_an(m)
        return (bool(gelesen and benutzt),
                ClothLichtTests._urteil(gelesen, benutzt))

    @staticmethod
    def test_warp_only_uses_payload_lights():
        """Gelesen wird `bakedatei` UND der Renderweg."""
        import collision.warp_render as m
        gelesen, benutzt = ClothLichtTests._lichter_kommen_an(m)
        return (bool(gelesen and benutzt),
                ClothLichtTests._urteil(gelesen, benutzt))

    @staticmethod
    def test_warp_only_reads_segment_color_from_bake():
        """warp_render muss pro Segment die Farbe aus dem Bake lesen (seg.get('color')),
        nicht stur Magenta zuweisen."""
        import collision.warp_render as wr
        src = inspect.getsource(wr)
        liest = any(marke in src
                    for marke in ClothLichtTests.SEGMENTFARBE)
        return liest, ('OK (Farbe aus bake-seg)' if liest
                       else 'Cloth-Farbe nicht aus Bake gelesen')

    @staticmethod
    def test_blender_eevee_reads_segment_color_from_scene():
        """Auch der EEVEE-Weg muss die Farben aus der Szene nehmen.

        DIESE PRUEFUNG FEHLTE (01.09.2026). Fuer `warp_blender` und
        `warp_only` gab es je eine; der dritte Motor blieb ungeprueft
        und hat jede Kleidung magenta gerendert, waehrend dieselbe
        Szene in den beiden anderen Motoren die vom Nutzer gewaehlte
        Farbe zeigte. Die Farben lagen in der Datei — `load_scene` las
        sie nur nicht mit.

        Gelesen werden BEIDE Stellen: das Einlesen der Szene
        (`blender_geometrie`, jetzt ueber `Bakedatei`) und das Setzen
        des Materials (`blender_stoff`). Eine allein genuegt nicht: Wer
        die Farbe liest und dann doch den festen Wert setzt, faellt
        sonst durch das Raster.
        """
        import collision.blender_stoff as bs
        import collision.bakedatei as bd
        stoff = inspect.getsource(bs)
        datei = inspect.getsource(bd)
        setzt = any(marke in stoff
                    for marke in ClothLichtTests.SEGMENTFARBE)
        liest = any(marke in datei
                    for marke in ("'seg%d_color' % i", 'seg{i}_color',
                                  "seg%d_color"))
        ok = setzt and liest
        return (ok, 'OK (Farbe aus der Szene)' if ok
                else ('Farbe wird nicht gesetzt' if not setzt
                      else 'Farbe wird beim Lesen der Szene verworfen'))

    @staticmethod
    def test_blender_eevee_reads_body_color_from_scene():
        """Und die Koerperfarbe genauso — mit EINER Rueckfallfarbe.

        Drei Renderwege hatten zwei verschiedene Rueckfall-Hauttoene
        (0.85 vs 0.88). Sie stehen jetzt als `Bakedatei.HAUT`
        beziehungsweise `.STOFF` an einer Stelle.
        """
        import collision.blender_stoff as bs
        import collision.warp_render as wr
        import collision.blender_render_from_bake as brb
        quellen = (inspect.getsource(bs) + inspect.getsource(wr)
                   + inspect.getsource(brb))
        eigene = [z for z in quellen.splitlines()
                  if '0.88, 0.78, 0.72' in z or '0.85, 0.78, 0.72' in z
                  or '0.92, 0.35, 0.55' in z]
        nutzt = quellen.count('Bakedatei.HAUT') >= 3
        ok = nutzt and not eigene
        return (ok, 'OK (eine Rueckfallfarbe fuer alle drei Motoren)'
                if ok else 'eigene Farbwerte uebrig: %s' % eigene[:3])

    @staticmethod
    def test_warp_blender_reads_segment_color_from_bake():
        """blender_render_from_bake muss pro Segment die Farbe aus dem Bake lesen."""
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(brb)
        liest = any(marke in src
                    for marke in ClothLichtTests.SEGMENTFARBE)
        return liest, ('OK (Farbe aus bake-seg)' if liest
                       else 'Cloth-Farbe nicht aus Bake gelesen')

    @staticmethod
    def test_warp_blender_lights_preserved_from_payload():
        """setup_lights_from_payload muss pro Licht ein Blender-Light-Object erstellen
        mit passendem Typ (SPOT/SUN/POINT) — matcht sowohl Payload-Typ-Strings als auch
        Blender-Typ-Enum-Werte.

        Gelesen wird `blender_kamera`, nicht mehr
        `blender_render_from_bake`: Seit dem 01.09.2026 steht die
        Lichter-Logik dort EINMAL statt in beiden Renderwegen. Der
        Renderweg ruft sie nur noch auf.
        """
        import collision.blender_kamera as bk
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(bk) + inspect.getsource(brb)
        has_spot = "'SPOT'" in src or '"SPOT"' in src
        has_sun = "'SUN'" in src or '"SUN"' in src
        has_point = "'POINT'" in src or '"POINT"' in src
        ok = has_spot and has_sun and has_point
        return (
            ok,
            'OK' if ok
            else (f'Licht-Typen unvollständig (SPOT={has_spot} '
                  f'SUN={has_sun} POINT={has_point})'))
