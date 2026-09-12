# -*- coding: utf-8 -*-
u"""Der Klick auf ein Kleidungsstueck und die Namen der Reiter.

DREI BEFUNDE VOM 09.09.2026, alle aus derselben Sitzung:

1. „Klick auf die Hose aendert den Tab zu Eigenschaften des Modells. Es soll
   zu GarmenCode wechseln!" — `_doSubMeshClick` schaltete fest auf
   `eigenschaften`.
2. „Aendere die Namen der Tabs: «Modell» in «Skeleton», Eigenschaften zu
   «Modell»." Geaendert wird nur die BESCHRIFTUNG; die Kennung `data-tab`
   bleibt, denn an ihr haengen `localStorage`, die Servereinstellungen, der
   `Figurmerker` und die Tests.
3. „danach war das UI nicht mehr bedienbar, nur nach Refresh der ganzen
   Seite" — die Drapierung antwortete nie, und `Serverabruf.formular` sitzt
   ohne Frist auf `fetch`. Begruendung in `gemeinsam/fristabruf.js`.

Ein Test am Quelltext, weil alle drei Stellen im Browser laufen: Er faellt,
sobald jemand den festen Reiter zurueckbaut oder die Frist wieder entfernt.
"""
from pathlib import Path

from django.conf import settings
from unittest import skipUnless

from django.test import SimpleTestCase


def _js(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer'
            ).joinpath(*teile).read_text(encoding='utf-8')


def _da(*teile):
    u"""Liegt diese Datei (schon) im Baum?

    `garmentdeutung.js` gehoert zu einer parallelen Sitzung und ist zum
    Zeitpunkt dieses Commits noch nicht versioniert. Ein Test, der eine
    fehlende Datei liest, wuerde mit `FileNotFoundError` scheitern — und
    das saehe wie ein echter Befund aus.
    """
    return ((Path(settings.BASE_DIR) / 'static' / 'viewer')
            .joinpath(*teile).exists())


def _vorlage(name):
    return (Path(settings.BASE_DIR) / 'templates' / name
            ).read_text(encoding='utf-8')


class KlickAufEinStueck(SimpleTestCase):

    databases = set()

    def test_kein_fester_reiter_mehr(self):
        quelle = _js('scene', 'teilnetz_auswahl.js')
        self.assertNotIn("switchTab('eigenschaften')", quelle,
                         u'Der Reiter wird wieder fest gewaehlt — dann '
                         u'landet auch ein GarmentCode-Stueck dort.')

    def test_die_entscheidung_kommt_aus_der_zuordnung(self):
        quelle = _js('scene', 'teilnetz_auswahl.js')
        self.assertIn('Reiterzuordnung', quelle)
        self.assertIn('Reiterzuordnung.fuer(', quelle)

    def test_die_vorlage_wird_mitgesetzt(self):
        u"""Ein Reiter mit den Reglern eines ANDEREN Stuecks hilft nicht."""
        self.assertIn('garmentcodeVorlageZeigen',
                      _js('scene', 'teilnetz_auswahl.js'))
        self.assertIn('fn.garmentcodeVorlageZeigen',
                      _js('scene', 'garmentcode.js'))

    @skipUnless(_da('scene', 'garmentdeutung.js'),
                u'garmentdeutung.js liegt noch nicht im Baum (parallele '
                u'Sitzung, 09.09.2026).')
    def test_die_deutung_setzt_die_auswahl_STILL(self):
        u"""Und das ist eine Entscheidung, kein Versehen — gemessen.

        Erst lief sie hier ueber `vorlageZeigen`, also mit `change`. Am
        `change` haengt seit dem 09.09.2026 auch das `Reitergedaechtnis`,
        und dessen `localStorage` ist ueber ALLE Tabs derselben Herkunft
        geteilt: Im Versuch stand danach in einem fremden Tab
        „sommerkleid", weil hier ein Sommerkleid gedeutet worden war.

        Die Deutung ist eine ABLEITUNG aus einem Bibliotheksstueck, keine
        Einstellung des Nutzers. Sie laedt die Regler gleich darunter
        selbst; ein Ereignis braucht sie nicht.
        """
        quelle = _js('scene', 'garmentdeutung.js')
        self.assertIn('auswahl.value = deutung.vorlage', quelle)
        self.assertNotIn('garmentcodeVorlageZeigen', quelle,
                         u'Die Deutung darf die Vorlage nicht merken lassen.')
        self.assertIn('garmentcodeRegler.laden(deutung.vorlage)', quelle,
                      u'Ohne das Nachladen zeigte der Reiter die Regler des '
                      u'vorigen Stuecks.')

    def test_vorlage_zeigen_loest_das_ereignis_aus(self):
        quelle = _js('scene', 'garmentcode.js')
        self.assertIn("dispatchEvent(new Event('change'", quelle)


class Reiternamen(SimpleTestCase):

    databases = set()

    #: Kennung -> sichtbare Beschriftung (Edgar, 09.09.2026).
    NAMEN = {'eigenschaften': 'Modell', 'modell': 'Skeleton'}

    def test_die_beschriftungen_stehen_so_da(self):
        seite = _vorlage('scene_config.html')
        for kennung, name in Reiternamen.NAMEN.items():
            self.assertIn('data-tab="%s">%s</div>' % (kennung, name), seite,
                          u'Reiter „%s" heisst nicht „%s".' % (kennung, name))

    def test_die_kennungen_bleiben(self):
        u"""An ihnen haengen `localStorage`, Einstellungen und Figurmerker.

        Sie umzubenennen haette jede gemerkte Reiterwahl entwertet — und
        zwar still: Ein unbekannter Reitername faellt einfach auf die
        Vorgabe zurueck.
        """
        seite = _vorlage('scene_config.html')
        for kennung in ('eigenschaften', 'modell'):
            self.assertIn('id="tab-%s"' % kennung, seite)


class Fristen(SimpleTestCase):

    databases = set()

    #: Datei -> die Anfrage, die eine Frist braucht.
    LANGE_ANFRAGEN = {
        'garmentcode_drapieren.js': '/api/garmentcode/drapieren/',
        'garmentcode_schnitt.js': '/api/garmentcode/erzeugen/',
    }

    def test_die_bauanfragen_haben_eine_frist(self):
        for datei, adresse in Fristen.LANGE_ANFRAGEN.items():
            quelle = _js('scene', datei)
            self.assertIn('Fristabruf.formular(', quelle, datei)
            self.assertIn(adresse, quelle, datei)
            self.assertNotIn('Serverabruf.formular(', quelle,
                             u'%s wartet wieder ohne Frist — ein Bau, dessen '
                             u'Antwort ausbleibt, sperrt alle Knoepfe.' % datei)

    def test_die_frist_ist_laenger_als_die_laengste_gemessene_drapierung(self):
        u"""66,09 s am 09.09.2026, 12:32. Alles darunter braeche gute Laeufe ab."""
        quelle = _js('gemeinsam', 'fristabruf.js')
        zeile = [z for z in quelle.splitlines() if 'FRIST_S =' in z][0]
        sekunden = int(zeile.split('=')[1].strip().rstrip(';'))
        self.assertGreaterEqual(sekunden, 120)

    def test_djangobase_bleibt_unberuehrt(self):
        u"""Das Paket haengt in sechs Projekten (`A:/shared/djangoBase`)."""
        quelle = _js('gemeinsam', 'fristabruf.js')
        self.assertIn("from './serverabruf.js'", quelle)
