# -*- coding: utf-8 -*-
u"""Ein Klick auf eine Pose legt sie an — und sagt, wenn er es nicht kann.

BEFUND (Edgar, 09.09.2026): „sind die im Tab Menue - Pose? wenn ich da auf
eine Pose klicke, wird die nicht angewandt auf das aktuelle Modell."

Er hatte recht, und zwar doppelt:

1. Der Einfachklick WAEHLTE nur aus (`_auswaehlen`); angewandt wurde die Pose
   per Doppelklick oder Kontextmenue. Nirgends sonst im Projekt ist das so —
   die beiden Animationsbaeume (`animation/baum.js`,
   `skelett_test/animationsbaum.js`) laden beim einfachen Klick.
2. `Posenanwendung.vomServer` kehrte an FUENF Stellen wortlos zurueck: keine
   Figur gewaehlt, Figur nicht gehaeutet, Serverfehler, kein Skelett, kein
   Knochenname getroffen. Von aussen sah jeder dieser Faelle genauso aus wie
   ein Knopf, der nicht funktioniert.

Der zweite Punkt trifft besonders die anderen Figurarten: Posen sind Deltas
auf RIGIFY-Knochennamen (`DEF-thigh.L`). Eine SMPL-, MakeHuman- oder
UMA-Figur fuehrt ihr eigenes Skelett (`Pelvis`, `Spine1`); dort passt kein
einziger Name, und `anwenden` setzte still null Knochen.

WARUM AM QUELLTEXT GEMESSEN
===========================
Beide Module haengen ueber `state.js`/`skeleton.js` an Three.js und laufen
nicht unter node — ein Rechentest wie `test_js_greifrechnung` ist nicht
moeglich. Geprueft wird deshalb genau das, was hier still schiefgeht: dass
der Klick anwendet, dass kein Ausstieg schweigt, und dass es die Statuszeile
gibt, in die geschrieben wird.

GEGENPROBE (09.09.2026, von Hand gemacht): Alle vier Faelle gegen die alte
Fassung aus `git show HEAD:...` gelaufen — alle vier werden rot.
"""
import io

from django.conf import settings
from django.test import SimpleTestCase


def _quelle(pfad):
    voll = settings.BASE_DIR / 'static' / 'viewer' / pfad
    return io.open(voll, encoding='utf-8').read()


def _vorlage():
    voll = settings.BASE_DIR / 'templates' / 'scene_config.html'
    return io.open(voll, encoding='utf-8').read()


class PosenklickTest(SimpleTestCase):
    u"""Der Klick loest aus, nicht der Doppelklick."""

    def test_die_zeile_wendet_beim_klick_an(self):
        quelle = _quelle('scene/pose_apply.js')
        # Der Klickhoerer der Zeile steht in `_zeileBauen`; er muss neben der
        # Auswahl auch das Anwenden rufen.
        block = quelle.split('function _zeileBauen')[1]
        hoerer = block.split("addEventListener('click'")[1].split('});')[0]
        self.assertIn('_auswaehlen', hoerer,
                      u'Der Klick muss die Zeile weiter markieren.')
        self.assertIn('_anwenden', hoerer,
                      u'Der Klick auf eine Posenzeile muss die Pose anlegen — '
                      u'genau das fehlte bis zum 09.09.2026.')

    def test_kein_doppelklick_als_einziger_weg(self):
        u"""Ein `dblclick` neben dem Klick loeste dreimal aus.

        Bei einem Doppelklick feuert `click` zweimal UND `dblclick` — das
        waeren drei Serverabrufe und dreimal dieselbe Rechnung.
        """
        quelle = _quelle('scene/pose_apply.js')
        self.assertNotIn('dblclick', quelle)

    def test_jeder_ausstieg_nennt_seinen_grund(self):
        u"""`vomServer` und `zuruecksetzen` duerfen nicht schweigen."""
        quelle = _quelle('scene/posenanwendung.js')
        koepfe = {'vomServer': 'static async vomServer(',
                  'zuruecksetzen': 'static zuruecksetzen('}
        for name, kopf in koepfe.items():
            self.assertIn(kopf, quelle)
            rumpf = quelle.split(kopf)[1].split('    /**')[0]
            self.assertNotIn('return;', rumpf,
                             u'%s kehrt wortlos zurueck — von aussen '
                             u'sieht das aus wie ein kaputter Knopf.'
                             % name)
            self.assertIn('grund', rumpf,
                          u'%s muss einen Grund liefern.' % name)

    def test_fremde_figurarten_werden_erkannt(self):
        u"""Die Pruefung schaut auf `quelle` — das Merkmal der Figurart."""
        quelle = _quelle('scene/posenanwendung.js')
        pruefung = quelle.split('static pruefen(')[1].split('\n    }')[0]
        self.assertIn('figur.quelle', pruefung,
                      u'Nur die HumanBody-Figur hat kein `quelle`; alle '
                      u'anderen Arten fuehren ein eigenes Skelett.')
        self.assertIn('HumanBody', pruefung,
                      u'Die Meldung muss sagen, fuer wen Posen gelten.')

    def test_ohne_treffer_gilt_es_als_fehlschlag(self):
        u"""Null gesetzte Knochen ist kein Erfolg.

        Der Fall, der bei SMPL/MakeHuman/UMA eintritt, wenn die Pruefung
        einmal durchgelassen wuerde: `anwenden` laeuft durch und setzt nichts.
        """
        quelle = _quelle('scene/posenanwendung.js')
        stellen = quelle.split('static _stellen(')[1].split('\n    }')[0]
        self.assertIn('if (!gesetzt)', stellen)

    def test_die_statuszeile_gibt_es(self):
        self.assertIn('id="pose-status"', _vorlage())
        self.assertIn("getElementById('pose-status')",
                      _quelle('scene/pose_apply.js'))

    def test_auch_der_weg_aus_dem_hauptmenue_meldet(self):
        u"""T-Pose/A-Pose kommen aus `menubar.js` ueber diese Funktion."""
        quelle = _quelle('scene/pose_apply.js')
        rumpf = quelle.split('export async function applyPoseFromServer')[1]
        rumpf = rumpf.split('\n}')[0]
        self.assertIn('_status', rumpf)
