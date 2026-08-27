# -*- coding: utf-8 -*-
"""Fünf Klassen, die auf einem Arbeitsweg lagen und in keinem Test standen.

ANLASS: Das Werkzeug `testdeckung` meldet Klassen, die von einem Endpunkt aus
erreichbar sind und in keiner Prüfdatei erwähnt werden. Fünf davon gehören uns
selbst (der Rest sind Kopien im Vergleichs-Sandkasten `TestCharakter/`):

    Ladeschloss        core/daten/ladeschloss.py
    Pfadwurzeln        core/daten/pfadwurzeln.py
    Kleidungsregler    core/daten/kleidungsregler.py
    Retargetwahl       core/daten/retargetwahl.py
    TimestampedStream  core/logging_utils.py

Geprüft wird jeweils das, was beim Lesen NICHT offensichtlich ist — nicht die
Konstruktoren. Bei `Ladeschloss` ist das die doppelte Prüfung unter dem Schloss,
bei `TimestampedStream` das Puffern bis zum Zeilenende, bei den drei
Wertklassen die Frage, welcher Wert am Ende gilt.
"""

import threading
import time

from django.test import SimpleTestCase, TestCase

from core.daten.kleidungsregler import Kleidungsregler
from core.daten.ladeschloss import Ladeschloss
from core.daten.pfadwurzeln import Pfadwurzeln
from core.daten.retargetwahl import Retargetwahl
from core.logging_utils import TimestampedStream


class Vorlagenattrappe:
    """Was `Kleidungsregler.aus_parametern` von einer Kleidervorlage liest."""

    def __init__(self, offset=0.01, stiffness=0.4, color=(0.1, 0.2, 0.3)):
        self.offset = offset
        self.stiffness = stiffness
        self.color = color


class LadeschlossTest(SimpleTestCase):
    """Das Schloss je Name — und der zweite Blick darunter."""

    def test_gleicher_name_gleiches_schloss(self):
        schloss = Ladeschloss()
        self.assertIs(schloss.fuer('netz'), schloss.fuer('netz'))

    def test_verschiedene_namen_verschiedene_schloesser(self):
        """DER GRUND, WARUM ES DIESE KLASSE GIBT.

        Mit EINEM Schloss für alles wartete jede Anfrage auf die 1,21 s der
        Catmull-Clark-Unterteilung — auch die, die nur Morphdaten wollte.
        """
        schloss = Ladeschloss()
        self.assertIsNot(schloss.fuer('netz'), schloss.fuer('unterteiler'))

    def test_derselbe_faden_darf_zweimal_hinein(self):
        """`unterteiler()` braucht beim Füllen `netzdaten()` — RLock, nicht Lock."""
        schloss = Ladeschloss().fuer('netz')
        with schloss:
            self.assertTrue(schloss.acquire(blocking=False),
                            'ein einfacher Lock würde sich hier selbst sperren')
            schloss.release()

    def test_gebaut_wird_genau_einmal(self):
        """Der zweite Blick INNERHALB des Schlosses ist der Punkt.

        Zwei Fäden treffen gleichzeitig ein; der erste baut. Der zweite darf
        NICHT noch einmal bauen, auch wenn er beim ersten Blick nichts sah.
        """
        schloss = Ladeschloss()
        wert = {}
        gebaut = []
        losgehts = threading.Event()

        def bauen():
            gebaut.append(1)
            time.sleep(0.05)          # der zweite Faden laeuft hier auf
            wert['x'] = 'fertig'
            return wert['x']

        def holen():
            losgehts.wait()
            schloss.einmal('x', lambda: wert.get('x'), bauen)

        faeden = [threading.Thread(target=holen) for _ in range(4)]
        for faden in faeden:
            faden.start()
        losgehts.set()
        for faden in faeden:
            faden.join()
        self.assertEqual(len(gebaut), 1,
                         'gebaut wurde %dx statt einmal' % len(gebaut))

    def test_vorhandenes_wird_nicht_neu_gebaut(self):
        schloss = Ladeschloss()
        gebaut = []
        ergebnis = schloss.einmal('x', lambda: 'schon da',
                                  lambda: gebaut.append(1))
        self.assertEqual(ergebnis, 'schon da')
        self.assertEqual(gebaut, [])


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


class KleidungsreglerTest(SimpleTestCase):
    """Welcher Wert gilt: der aus der Anfrage oder der aus der Vorlage?"""

    def test_anfrage_schlaegt_vorlage(self):
        regler = Kleidungsregler.aus_parametern(
            {'offset': '0.02', 'stiffness': '0.9'}, Vorlagenattrappe())
        self.assertAlmostEqual(regler.abstand, 0.02)
        self.assertAlmostEqual(regler.steifigkeit, 0.9)

    def test_ohne_angabe_gilt_die_vorlage(self):
        regler = Kleidungsregler.aus_parametern({}, Vorlagenattrappe())
        self.assertAlmostEqual(regler.abstand, 0.01)
        self.assertAlmostEqual(regler.steifigkeit, 0.4)

    def test_unbrauchbarer_wert_faellt_auf_die_vorgabe_zurueck(self):
        """„unbrauchbar → Vorgabe" ist die Vorschrift dieser Klasse.

        Ein Regler kommt aus der Abfragezeichenkette; `offset=viel` darf keine
        Fehlerseite ergeben, sondern die Vorlage.
        """
        for kaputt in ('viel', '', None, 'NaN?'):
            with self.subTest(wert=kaputt):
                regler = Kleidungsregler.aus_parametern(
                    {'offset': kaputt}, Vorlagenattrappe())
                self.assertAlmostEqual(regler.abstand, 0.01)

    def test_farbe_kanalweise_ueberschreibbar(self):
        regler = Kleidungsregler.aus_parametern({'color_g': '0.75'},
                                                Vorlagenattrappe())
        self.assertAlmostEqual(regler.farbe[0], 0.1)
        self.assertAlmostEqual(regler.farbe[1], 0.75)
        self.assertAlmostEqual(regler.farbe[2], 0.3)

    def test_um_huelle_nur_bei_rig_hull(self):
        self.assertTrue(Kleidungsregler.aus_parametern(
            {'fit_mode': 'rig_hull'}, Vorlagenattrappe()).um_huelle)
        self.assertFalse(Kleidungsregler.aus_parametern(
            {'fit_mode': 'body'}, Vorlagenattrappe()).um_huelle)
        self.assertFalse(Kleidungsregler.aus_parametern(
            {}, Vorlagenattrappe()).um_huelle)


class RetargetwahlTest(SimpleTestCase):
    """`delta_norm` ist DREIWERTIG — das ist der ganze Punkt."""

    def test_drei_zustaende(self):
        self.assertIs(Retargetwahl({'delta_norm': '1'}, 1.68).delta_norm, True)
        self.assertIs(Retargetwahl({'delta_norm': '0'}, 1.68).delta_norm, False)
        self.assertIsNone(Retargetwahl({}, 1.68).delta_norm,
                          'ohne Angabe entscheidet das Format')
        self.assertIsNone(Retargetwahl({'delta_norm': 'vielleicht'},
                                       1.68).delta_norm)

    def test_groesse_und_fusskorrektur(self):
        wahl = Retargetwahl({'body_height': '1.80',
                             'foot_correction': 'TRUE'}, 1.68)
        self.assertAlmostEqual(wahl.groesse, 1.80)
        self.assertTrue(wahl.fusskorrektur)

    def test_vorgabe_greift(self):
        wahl = Retargetwahl({}, 1.68)
        self.assertAlmostEqual(wahl.groesse, 1.68)
        self.assertFalse(wahl.fusskorrektur)
        self.assertIsNone(wahl.format)


class Sammelstrom:
    """Attrappe fuer stdout — merkt sich, was geschrieben wurde."""

    def __init__(self):
        self.stuecke = []

    def write(self, text):
        self.stuecke.append(text)
        return len(text)

    def flush(self):
        pass

    @property
    def text(self):
        return ''.join(self.stuecke)


class TimestampedStreamTest(SimpleTestCase):
    """Zeitstempel je ZEILE — und nichts vor dem Zeilenende."""

    def test_haelt_zurueck_bis_zum_zeilenende(self):
        """DER GRUND FUER DEN PUFFER.

        Ohne ihn bekäme jeder Teil-Schreibvorgang einen eigenen Zeitstempel —
        eine tqdm-Fortschrittsleiste würde damit unlesbar.
        """
        ziel = Sammelstrom()
        strom = TimestampedStream(ziel)
        strom.write('halb')
        self.assertEqual(ziel.text, '', 'ohne Zeilenende darf nichts raus')
        strom.write(' fertig\n')
        self.assertIn('halb fertig', ziel.text)

    def test_zeitstempel_wird_vorangestellt(self):
        ziel = Sammelstrom()
        TimestampedStream(ziel).write('eine Zeile\n')
        self.assertRegex(ziel.text, r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ')

    def test_vorhandener_zeitstempel_wird_nicht_verdoppelt(self):
        ziel = Sammelstrom()
        TimestampedStream(ziel).write('2026-08-27 10:00:00 schon da\n')
        self.assertEqual(ziel.text.count('2026-08-27'), 1)

    def test_flush_gibt_den_rest_heraus(self):
        ziel = Sammelstrom()
        strom = TimestampedStream(ziel)
        strom.write('ohne Zeilenende')
        strom.flush()
        self.assertIn('ohne Zeilenende', ziel.text)

    def test_unbekannte_namen_gehen_an_den_umschlossenen_strom(self):
        """`__getattr__` reicht durch — sonst bricht `sys.stdout.isatty()`."""
        ziel = Sammelstrom()
        ziel.encoding = 'utf-8'
        self.assertEqual(TimestampedStream(ziel).encoding, 'utf-8')
