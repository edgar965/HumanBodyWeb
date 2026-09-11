# -*- coding: utf-8 -*-
u"""`Shaderpatch`: zwei Eingriffe in denselben Shader, ohne dass der zweite
den ersten löscht — geprüft in Node, mit dem echten Modul.

WARUM (11.09.2026): Weichgewebe (`zuschlag`) und Hautverdeckung (`einzug`)
patchen beide das Körpermaterial. Three.js kennt je Material EIN
`onBeforeCompile`; wer als Zweiter kommt, löscht den Ersten still. Und
`Material.clone()` nimmt weder `onBeforeCompile` noch den Programmschlüssel
mit — nach dem Klonen im Weichgewebe wäre der Einzug weg gewesen.

Sabotage-Gegenprobe: `for (const fn of eintraege.values()) fn(...)` →
nur den letzten rufen macht Fall 1 rot; `klonen` ohne Register-Kopie macht
Fall 2 rot; Programmschlüssel fest `'x'` macht Fall 3 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'shaderpatch.js')

SKRIPT = """
const { Shaderpatch } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };
// Ein Material-Ersatz: clone() wie Three.js — OHNE onBeforeCompile.
const material = () => ({ isMaterial: true, needsUpdate: false, clone() { return material(); } });
const shader = () => ({ vertexShader: '#include <common>\\n#include <begin_vertex>\\n#include <skinning_vertex>\\n' });

// --- 1. Zwei Eingriffe, beide wirken ---------------------------------------
const m = material();
Shaderpatch.anhaengen(m, 'hauteinzug', (s) => Shaderpatch.hinterInclude(s, 'begin_vertex', 'transformed += einzug;'));
Shaderpatch.anhaengen(m, 'weichgewebe', (s) => Shaderpatch.hinterInclude(s, 'skinning_vertex', 'transformed += zuschlag;'));
let s = shader(); m.onBeforeCompile(s);
if (!s.vertexShader.includes('transformed += einzug;')) fehl('erster Eingriff weg');
if (!s.vertexShader.includes('transformed += zuschlag;')) fehl('zweiter Eingriff weg');
if (s.vertexShader.indexOf('einzug') > s.vertexShader.indexOf('zuschlag')) fehl('Einzug muss VOR dem Skinning stehen');
if (!m.needsUpdate) fehl('needsUpdate nicht gesetzt');
if (!Shaderpatch.hat(m, 'weichgewebe') || Shaderpatch.hat(m, 'fremd')) fehl('hat() falsch');

// --- 2. Klonen nimmt die Eingriffe mit, clone() allein nicht ---------------
const k = Shaderpatch.klonen(m);
s = shader(); k.onBeforeCompile(s);
if (!s.vertexShader.includes('einzug') || !s.vertexShader.includes('zuschlag')) fehl('Klon ohne Eingriffe');
const nackt = m.clone();
if (typeof nackt.onBeforeCompile === 'function') fehl('Attrappe: clone() darf onBeforeCompile nicht kopieren');
// Ein weiterer Eingriff am Klon erreicht das Original nicht.
Shaderpatch.anhaengen(k, 'dritter', (s2) => { s2.vertexShader += 'dritter'; });
s = shader(); m.onBeforeCompile(s);
if (s.vertexShader.includes('dritter')) fehl('Klon teilt das Register mit dem Original');

// --- 3. Der Programmschlüssel nennt alle Eingriffe, sortiert ----------------
if (m.customProgramCacheKey() !== 'hauteinzug+weichgewebe') fehl('Schluessel ' + m.customProgramCacheKey());
if (k.customProgramCacheKey() !== 'dritter+hauteinzug+weichgewebe') fehl('Schluessel Klon ' + k.customProgramCacheKey());
const einer = Shaderpatch.anhaengen(material(), 'weichgewebe', () => {});
if (einer.customProgramCacheKey() === m.customProgramCacheKey()) fehl('verschiedene Eingriffe, gleicher Schluessel');

// --- 4. hinterInclude meldet ein fehlendes Include ------------------------
if (Shaderpatch.hinterInclude(shader(), 'gibt_es_nicht', 'x')) fehl('fehlendes Include gilt als eingefuegt');

console.log(JSON.stringify({ ok: true, schluessel: Shaderpatch.schluessel(k) }));
"""


class ShaderpatchTest(SimpleTestCase):

    databases = []

    def test_zwei_eingriffe_klonen_und_schluessel(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['schluessel'], ['dritter', 'hauteinzug', 'weichgewebe'])
