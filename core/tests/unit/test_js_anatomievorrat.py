# -*- coding: utf-8 -*-
u"""`Anatomievorrat` — der Schlüssel der Scham-Karten, auch wenn eine Haut-Gruppe einen Platzhalter trägt (19.10.2026).

Gemessen an DamiraAlt (/Charakter/, F5): die Körpergruppe hat keine eigene Normalenkarte, die Hautebenen setzen die flache 1×1 von `Genesis9haut.platzhalter`
ein — sie hatte keine Adresse, `schluessel` gab null, die Karten wurden bei jedem Laden neu gerechnet („Hautfarbe" 6–8 s nach allem anderen).

1. `kennung`: Bild mit Adresse → die Adresse; kleiner erzeugter Platzhalter → sein Inhalt (Größe, Bytes, Farbraum); großes Bild ohne Adresse → null.
2. `schluessel`: mit Platzhalter ein Schlüssel nach dem Muster des Servers; derselbe für einen zweiten, gleichen Platzhalter (neues Objekt, wie nach jedem Laden);
   ein anderer, wenn der Platzhalter einen anderen Inhalt hat; null bei einem großen Bild ohne Adresse.

Sabotage (von Hand, nicht als Lauf): in `kennung` den Inhalt weglassen (nur `'daten'`) → Fall 2 rot („anderer Inhalt, anderer Schlüssel"). Geschrieben, nicht gelaufen.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'anatomievorrat.js')

SKRIPT = """
globalThis.window = globalThis.window || { addEventListener() {}, removeEventListener() {} };
globalThis.document = globalThis.document || { addEventListener() {}, removeEventListener() {}, dispatchEvent() { return true; }, cookie: '' };
const { Anatomievorrat: V } = await import(MODUL);
const bild = (adresse) => ({ userData: { adresse } });
const platzhalter = (r, g, b, a = 255) => ({ isDataTexture: true, userData: {}, colorSpace: '', image: { width: 1, height: 1, data: Uint8Array.from([r, g, b, a]) } });
const gross = { isDataTexture: true, userData: {}, colorSpace: '', image: { width: 64, height: 64, data: new Uint8Array(64 * 64 * 4) } };

// 1. kennung
pruefe('mit Adresse', V.kennung(bild('/api/x/haut.jpg')), '/api/x/haut.jpg');
pruefe('Platzhalter: Inhalt', V.kennung(platzhalter(128, 128, 255)), 'daten:1x1:128,128,255,255:');
pruefe('großes Bild ohne Adresse', V.kennung(gross), null);

// 2. schluessel
const stueck = { pos: Float32Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0]), uv: Float32Array.from([0, 0, 1, 0, 0, 1]), index: Uint32Array.from([0, 1, 2]), normal: Float32Array.from([0, 0, 1, 0, 0, 1, 0, 0, 1]) };
const haut = { pos: Float32Array.from([0, 0, 0.01, 1, 0, 0.01, 0, 1, 0.01]), uv: Float32Array.from([0, 0, 1, 0, 0, 1]), normal: null, ecken: Uint32Array.from([0, 1, 2]) };
const e = (normalMap) => ({ stueck, breite: 512, hoehe: 512, quelle: { haut, texturen: [{ map: bild('/api/x/body.jpg'), normalMap, roughnessMap: null }] } });
const netz = { geometry: { userData: {} } }, original = { karte: bild('/api/x/scham.jpg') };
const k1 = V.schluessel(netz, e(platzhalter(128, 128, 255)), original);
pruefe('mit Platzhalter ein Schlüssel', /^[a-z0-9]{8,64}$/.test(k1 || ''), true);
pruefe('gleicher Platzhalter, gleicher Schlüssel', V.schluessel(netz, e(platzhalter(128, 128, 255)), original), k1);
pruefe('anderer Inhalt, anderer Schlüssel', V.schluessel(netz, e(platzhalter(127, 128, 255)), original) !== k1, true);
pruefe('großes Bild ohne Adresse: keiner', V.schluessel(netz, e(gross), original), null);
console.log(JSON.stringify({ ok: true }));
"""


class AnatomievorratTest(SimpleTestCase):
    databases = set()

    def test_schluessel_mit_platzhalter(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
