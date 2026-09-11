# -*- coding: utf-8 -*-
u"""Kein ES-Modul benutzt einen Namen, den es weder importiert noch definiert.

Anlass (11.09.2026): `garmentcode_gemeinsam.js` rief
`GarmentcodeMaterial.aufStueck(...)`, ohne `GarmentcodeMaterial` zu
importieren. Kein Ladefehler, keine Konsolenzeile beim Start — erst beim
Einhaengen der fertig simulierten Stuecke flog `ReferenceError`, und die
Meldung im Reiter sagte „0 von 2 angezogen". Drei Laeufe lang (je 70 s)
sah das fuer Edgar aus wie „die Leggings wird nicht gebaut". Dieselbe
Fehlerklasse wie `~/.claude/rules/es-module-stumme-fehler.md`.

Beim ersten Lauf fand der Pruefer gleich einen zweiten Fall:
`bvh_studio/spurfigur.js` nutzte `Koerpernetz.materialsatz` ohne Import.

Was geprueft wird: `Name.` mit grossem Anfangsbuchstaben — Klassen und
Namensraeume. Lokale Grossbuchstaben-Namen (Parameter, Destrukturierung)
gelten als bekannt, ebenso die Browser- und Sprach-Globalen.
"""
import io
import os
import re

from django.conf import settings
from django.test import SimpleTestCase

BEKANNT = set('''THREE JSON Math Object Number Array Promise Date String Boolean
Symbol Map Set WeakMap WeakSet Float32Array Float64Array Uint8Array Uint16Array
Uint32Array Int32Array Int16Array Int8Array ArrayBuffer DataView Event
CustomEvent KeyboardEvent MouseEvent PointerEvent FormData URL URLSearchParams
Blob File FileReader Image ImageData Intl Reflect Proxy Error TypeError
RangeError Function RegExp Infinity NaN Node Element HTMLElement
HTMLCanvasElement OffscreenCanvas WebSocket XMLHttpRequest TextDecoder
TextEncoder AbortController Response Request Headers Atomics BigInt
DOMParser XMLSerializer MutationObserver ResizeObserver IntersectionObserver
Worker MediaRecorder MediaStream Audio AudioContext Path2D
CanvasRenderingContext2D WebGLRenderingContext WebGL2RenderingContext
Notification Navigator Window Document Location History Storage
BroadcastChannel DOMRect Touch TouchEvent DragEvent WheelEvent ClipboardEvent
InputEvent FocusEvent UIEvent CSS globalThis Crypto SubtleCrypto Performance
PerformanceObserver Screen'''.split())

NUTZUNG = re.compile(r'(?<![\w.$\'"`])([A-Z][A-Za-z0-9_]+)\s*\.(?!\.)')
DEFINITION = re.compile(
    r'(?:^|\n)\s*(?:export\s+)?(?:class|const|let|var|function|async function)'
    r'\s+([A-Z][A-Za-z0-9_]+)')
IMPORT = re.compile(
    r'import\s*\{([^}]*)\}\s*from|import\s+\*\s+as\s+(\w+)\s+from|import\s+(\w+)\s+from')
LOKAL = re.compile(r'(?:[(,{]\s*|=\s*\{[^}]*?)([A-Z][A-Za-z0-9_]+)\s*[,)=}]')


class Jsimporte:
    u"""Findet in einem Modul die grossen Namen ohne Import und Definition."""

    @staticmethod
    def ohne_kommentare_und_texte(quelle):
        quelle = re.sub(r'/\*.*?\*/', '', quelle, flags=re.S)
        quelle = re.sub(r'//[^\n]*', '', quelle)
        quelle = re.sub(r'`(?:\\.|[^`\\])*`', '``', quelle, flags=re.S)
        quelle = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", quelle)
        quelle = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', quelle)
        return quelle

    @classmethod
    def fehlende(cls, quelle):
        quelle = cls.ohne_kommentare_und_texte(quelle)
        bekannt = set(BEKANNT)
        for m in IMPORT.finditer(quelle):
            if m.group(1):
                for teil in m.group(1).split(','):
                    teil = teil.strip()
                    if teil:
                        bekannt.add(teil.split(' as ')[-1].strip())
            else:
                bekannt.add(m.group(2) or m.group(3))
        bekannt.update(m.group(1) for m in DEFINITION.finditer(quelle))
        bekannt.update(m.group(1) for m in LOKAL.finditer(quelle))
        return sorted({m.group(1) for m in NUTZUNG.finditer(quelle)} - bekannt)


class JsimporteTest(SimpleTestCase):

    databases = []

    WURZEL = settings.BASE_DIR / 'static' / 'viewer'

    def test_kein_modul_nutzt_einen_namen_ohne_import(self):
        befunde = {}
        gezaehlt = 0
        for ordner, _, dateien in os.walk(self.WURZEL):
            for name in dateien:
                if not name.endswith('.js'):
                    continue
                pfad = os.path.join(ordner, name)
                gezaehlt += 1
                fehlend = Jsimporte.fehlende(
                    io.open(pfad, encoding='utf-8').read())
                if fehlend:
                    befunde[os.path.relpath(pfad, self.WURZEL)] = fehlend
        self.assertGreater(gezaehlt, 200, 'der Statik-Baum ist nicht da, wo erwartet')
        self.assertEqual(befunde, {}, 'Namen ohne Import: %r' % befunde)

    def test_die_gegenprobe_findet_den_anlass(self):
        u"""Genau der Fall vom 11.09.2026 — ohne diese Probe koennte der
        Pruefer still nichts finden (`analysewerkzeuge.md`)."""
        quelle = (
            "import { A } from './a.js';\n"
            "export class B {\n"
            "    static x(figur, stueck) {\n"
            "        const bisher = GarmentcodeMaterial.getragen(figur, stueck);\n"
            "        return A.y(bisher) + Math.max(1, 2);\n"
            "    }\n"
            "}\n")
        self.assertEqual(Jsimporte.fehlende(quelle), ['GarmentcodeMaterial'])
        # Texte und Kommentare zaehlen nicht, lokale Namen auch nicht.
        harmlos = (
            "// Koerpernetz.materialsatz steht woanders\n"
            "const t = `${Foo.bar}`; const s = 'Baz.qux';\n"
            "function f(Vorlage, { Regler }) { return Vorlage.a + Regler.b; }\n")
        self.assertEqual(Jsimporte.fehlende(harmlos), [])
