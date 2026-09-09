# -*- coding: utf-8 -*-
u"""`Gedaechtniswahl`: was sich die Oberflaeche merken darf.

WARUM (Edgar, 09.09.2026: „merke dir die letzten Einstellungen auf allen Tabs,
z.B. GarmentCode, so dass sie beim naechsten Aufruf angeklickt sind")
=====================================================================
Im Bedienfeld stehen zwei Sorten Regler, und sie sehen gleich aus: die
EINSTELLUNG (welches Stueck gebaut wird, wie weit der Aermel sitzt) und der
OBJEKTZUSTAND (die 289 Morphschieber der Figur, `prop-garment-*` des
gewaehlten Kleides, Licht und Kamera der Szene).

Einen Objektzustand beim Start aus dem Gedaechtnis zu setzen ist der
schlimmere Fehler von beiden: Der Schieber behauptet dann etwas ueber das
Objekt, das nicht stimmt, und der erste Zug daran verformt es. Deshalb ist
die Liste eine POSITIVLISTE — und deshalb gibt es diesen Test: Er haelt
fest, dass die vier gesperrten Reiter gesperrt BLEIBEN.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
import io

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'gedaechtniswahl.js')

SKRIPT = """
const { Gedaechtniswahl } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};

// --- 1. Die erlaubten Reiter ----------------------------------------------
pruefe('garmentcode', Gedaechtniswahl.merkbar(
    {reiter: 'garmentcode', kennung: 'gc-vorlage', art: 'select-one'}), true);
pruefe('finalize', Gedaechtniswahl.merkbar(
    {reiter: 'finalize', kennung: 'fin-apply-pose', art: 'checkbox'}), true);

// --- 2. Objektzustand bleibt draussen -------------------------------------
// Der ganze Reiter „Eigenschaften": Morphs, Formregler, UMA-Groesse.
for (const kennung of ['morph-Torso_BreastMass', 'prop-garment-offset',
                       'smpl-beta0', 'uma-height']) {
    pruefe('eigenschaften/' + kennung, Gedaechtniswahl.merkbar(
        {reiter: 'eigenschaften', kennung, art: 'range'}), false);
}
// Kleider und Assets: Regler des GEWAEHLTEN Stuecks.
pruefe('kleider', Gedaechtniswahl.merkbar(
    {reiter: 'kleider', kennung: 'kld-offset', art: 'range'}), false);
pruefe('assets', Gedaechtniswahl.merkbar(
    {reiter: 'assets', kennung: 'hair-color', art: 'color'}), false);
// Szene: Licht und Kamera stehen in der Szenendatei.
pruefe('szene', Gedaechtniswahl.merkbar(
    {reiter: 'szene', kennung: 'light-intensity', art: 'range'}), false);
// Modell: der Generator fuehrt seinen eigenen Zustand.
pruefe('modell', Gedaechtniswahl.merkbar(
    {reiter: 'modell', kennung: 'mg-skeleton-type', art: 'select-one'}), false);

// --- 3. `prop-` ist auch in einem erlaubten Reiter gesperrt ---------------
// Die Eigenschaften des gewaehlten Netzes tauchen in mehreren Reitern auf.
pruefe('prop im erlaubten Reiter', Gedaechtniswahl.merkbar(
    {reiter: 'garmentcode', kennung: 'prop-garment-color', art: 'color'}),
    false);

// --- 4. Feldarten, die nicht gehen ---------------------------------------
for (const art of ['file', 'search', 'password', 'hidden', 'submit',
                   'button', 'reset']) {
    pruefe('art ' + art, Gedaechtniswahl.merkbar(
        {reiter: 'garmentcode', kennung: 'irgendwas', art}), false);
}

// --- 5. Ohne Kennung gibt es keinen Schluessel ---------------------------
// Genau so fallen die 289 Morphschieber heraus: Sie haben keine `id`.
for (const kennung of [null, undefined, '']) {
    pruefe('ohne Kennung', Gedaechtniswahl.merkbar(
        {reiter: 'garmentcode', kennung, art: 'range'}), false);
}
pruefe('ohne Reiter', Gedaechtniswahl.merkbar(
    {reiter: null, kennung: 'gc-vorlage', art: 'select-one'}), false);
pruefe('leeres Objekt', Gedaechtniswahl.merkbar({}), false);
pruefe('nichts', Gedaechtniswahl.merkbar(null), false);

// --- 6. Schluessel und Reitername ----------------------------------------
pruefe('schluessel', Gedaechtniswahl.schluessel('garmentcode', 'gc-vorlage'),
       'garmentcode/gc-vorlage');
pruefe('reitername', Gedaechtniswahl.reiterName('tab-garmentcode'),
       'garmentcode');
pruefe('ohne Praefix', Gedaechtniswahl.reiterName('garmentcode'),
       'garmentcode');
pruefe('leer', Gedaechtniswahl.reiterName(undefined), '');

// --- 7. Zwei Reiter, gleiche Kennung: verschiedene Schluessel ------------
// Sonst ueberschriebe ein Feld im einen Reiter das gleichnamige im anderen.
if (Gedaechtniswahl.schluessel('animation', 'x')
        === Gedaechtniswahl.schluessel('rigging', 'x')) {
    throw new Error('Der Schluessel unterscheidet die Reiter nicht');
}
console.log(JSON.stringify({ok: true}));
"""


class GedaechtniswahlTest(SimpleTestCase):

    databases = []

    def test_die_wahl_haelt_sich_an_die_regeln(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_die_gesperrten_reiter_stehen_im_modul(self):
        u"""Gegenprobe am Quelltext: Waere `REITER` leer, wuerde oben alles
        `false` liefern und die Faelle 2 bis 5 blieben gruen."""
        quelle = io.open(MODUL.pfad, encoding='utf-8').read()
        for reiter in ('garmentcode', 'animation', 'rigging', 'finalize'):
            self.assertIn("'%s'" % reiter, quelle)
        for gesperrt in ('eigenschaften', 'kleider', 'assets', 'szene',
                         'modell'):
            self.assertNotIn("'%s'," % gesperrt,
                             quelle.split('static REITER')[1].split(']')[0])
