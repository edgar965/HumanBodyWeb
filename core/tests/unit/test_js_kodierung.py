# -*- coding: utf-8 -*-
u"""`pufferZuBase64` — vier Fassungen auf eine, und die muss stimmen.

WARUM (28.08.2026, Befund `doppelcode`)
=======================================
Es gab VIER Kodierer in drei Bauarten. Zwei arbeiteten stückweise, die dritte
(`viewer/utils.js`) hängte Zeichen für Zeichen an eine Zeichenkette an: bei
70.851 Punkten sind das 850.212 Durchläufe. Jetzt gehen alle durch eine
Funktion — und die wird hier gegen Pythons `base64` gerechnet, nicht gegen
sich selbst.

DIE STELLEN, DIE WEHTUN
=======================
* **Der Versatz.** `subarray` liefert eine SICHT auf denselben Speicher, mit
  eigenem `byteOffset`. Wer den vergisst, kodiert den Anfang des Puffers statt
  des Ausschnitts — und der base64-Zeichenkette sieht man das nicht an.
  Nachgestellt: `puffer.byteOffset` durch `0` ersetzt → der Test wird rot.
* **Die Schrittweite.** `i += stueck` um eins daneben wiederholt oder
  überspringt Bytes. Nachgestellt: `i += stueck - 1` → rot.

NICHT geprüft — und das ehrlich gesagt: die Stückgröße SELBST. Jede Größe
liefert dieselbe Zeichenkette; 32.768 statt 32.767 zu setzen ist nachweislich
folgenlos (nachgestellt, Test blieb grün). Die Zahl steht dort gegen den
Aufrufstapel: `String.fromCharCode.apply` legt jedes Byte als eigenes Argument
ab, ein Puffer am Stück gibt `RangeError: Maximum call stack size exceeded`.
Das ist eine Grenze der Laufzeitumgebung, kein Rechenergebnis.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
import base64
import struct

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'kodierung.js')

SKRIPT = """
const { pufferZuBase64, float32ToBase64, uint32ToBase64, base64ToFloat32 }
    = await import(MODUL);

const zahlen = [];
for (let i = 0; i < 10000; i++) zahlen.push(i * 0.25 - 1000);
const f32 = new Float32Array(zahlen);              // 40.000 Bytes
const genau = new Float32Array(32768 / 4);         // genau eine Stueckgrenze
for (let i = 0; i < genau.length; i++) genau[i] = i;
const indizes = new Uint32Array([0, 1, 2, 7, 4294967295]);

// Ein Blick auf einen Ausschnitt: der Puffer darf nicht bei 0 anfangen muessen.
const ausschnitt = f32.subarray(5, 9);

console.log(JSON.stringify({
    lang: float32ToBase64(f32),
    genau: float32ToBase64(genau),
    indizes: uint32ToBase64(indizes),
    ausschnitt: pufferZuBase64(ausschnitt),
    hinundzurueck: Array.from(base64ToFloat32(float32ToBase64(f32)).slice(0, 5)),
}));
"""


class KodierungTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ergebnis = MODUL.laufen(SKRIPT)

    @staticmethod
    def _erwartet(werte, format_='f'):
        return base64.b64encode(struct.pack('<%d%s' % (len(werte), format_),
                                            *werte)).decode('ascii')

    def test_langer_puffer_ueber_die_stueckgrenze(self):
        u"""40.000 Bytes — mehr als ein Stück, und keine runde Zahl davon."""
        werte = [i * 0.25 - 1000 for i in range(10000)]
        self.assertEqual(self.ergebnis['lang'], self._erwartet(werte))

    def test_genau_eine_stueckgrenze(self):
        u"""32.768 Bytes: Der letzte Durchlauf holt exakt nichts mehr.

        Das fängt einen falschen SCHRITT ab (`i += stueck - 1`), nicht eine
        andere Stückgröße — die ist folgenlos, siehe Modulkopf."""
        werte = [float(i) for i in range(32768 // 4)]
        self.assertEqual(self.ergebnis['genau'], self._erwartet(werte))

    def test_uint32_wird_genauso_kodiert(self):
        u"""Der Typ spielt beim Kodieren keine Rolle — gelesen werden Bytes."""
        self.assertEqual(self.ergebnis['indizes'],
                         self._erwartet([0, 1, 2, 7, 4294967295], 'I'))

    def test_ausschnitt_beachtet_den_versatz(self):
        u"""`subarray` liefert eine SICHT auf denselben Speicher. Wer
        `byteOffset` vergisst, kodiert den Anfang des Puffers statt des
        Ausschnitts — und niemand sieht es der base64-Zeichenkette an."""
        werte = [i * 0.25 - 1000 for i in range(5, 9)]
        self.assertEqual(self.ergebnis['ausschnitt'], self._erwartet(werte))

    def test_hin_und_zurueck(self):
        werte = [i * 0.25 - 1000 for i in range(5)]
        for ist, soll in zip(self.ergebnis['hinundzurueck'], werte):
            self.assertAlmostEqual(ist, soll, places=4)
