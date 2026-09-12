# -*- coding: utf-8 -*-
u"""Findet Bedienelemente, die kein Skript je anfasst.

DIE FEHLERKLASSE (`~/.claude/rules/es-module-stumme-fehler.md`): Der Knopf
steht da, die Seite lädt mit 200, die Konsole schweigt — und ein Klick tut
nichts. Kein Test bemerkt das, kein Blick auf die Seite auch nicht.

Anlass war Edgars Frage am 09.09.2026: „kannst du nicht alles durchtesten,
jeden Button und testen ob der das tut was er soll?"

DREI FEHLALARM-KLASSEN sind ausgeschlossen, jede an einem echten Fall belegt
(`~/.claude/rules/analysewerkzeuge.md` — erst nachsehen, dann urteilen):

1. **Zusammengesetzte Kennungen.** `${vorsilbe}-roughness`,
   `prop-garment-region-${rid}`, oder ein Präfix, an das etwas angehängt wird
   (`['mg-head-off-', …]` plus 'x'/'y'/'z'). Wörtlich gesucht wären das
   allein auf der Szene-Seite über 60 Fehlmeldungen.
2. **Formularfelder.** Ein `<input name="…">` wird SERVERSEITIG im POST
   gelesen und braucht keinen Hörer — `settings_bvh_studio.html` führt fünf
   davon.
3. **Delegierte Hörer.** `document.querySelectorAll('.cloth-export-btn')`
   greift vier Knöpfe über ihre Klasse, `.btn-texture[data-backend]` einen
   weiteren über sein data-Attribut.

Ohne diese drei Filter meldete der erste Lauf 59 Fälle, von denen vier echt
waren.
"""
import io
import re
from pathlib import Path

# Anzeigefelder neben einem Regler: `_bindSlider(id, id + '-val', …)` bedient
# sie, sie tragen nie einen eigenen Hörer.
ANZEIGE = re.compile(r'-val$')

# Fremdcode: `vendor` ist three.js & Co.
FREMD = ('vendor',)

PLATZHALTER = r'\$\{[^}]+\}'

ELEMENT = re.compile(
    r'<(input|select|button|textarea)\b([^>]*)\bid="([^"]+)"([^>]*)>', re.I)


class Bedienelemente:
    u"""Die Bedienelemente einer Seite und ihre Hörer."""

    def __init__(self, wurzel):
        self.vorlagen = Path(wurzel) / 'templates'
        self.statik = Path(wurzel) / 'static'
        self._code = None

    # ------------------------------------------------------------- Sammeln

    def seiten(self):
        u"""Vorlagen, die selbst eine Seite sind — am Modul-Einstieg erkannt."""
        namen = []
        for pfad in sorted(self.vorlagen.glob('*.html')):
            if 'type="module"' in io.open(pfad, encoding='utf-8').read():
                namen.append(pfad.name)
        return namen

    def kette(self, start):
        u"""Die Seite und alles, was sie einbindet — rekursiv."""
        offen, gesehen = [start], []
        while offen:
            name = offen.pop()
            pfad = self.vorlagen / name
            if not pfad.is_file() or name in gesehen:
                continue
            gesehen.append(name)
            # in der Schleife gewollt: je Durchlauf eine andere Vorlage
            text = io.open(pfad, encoding='utf-8').read()
            offen.extend(re.findall(r'{%\s*include\s+"([^"]+)"', text))
        return gesehen

    def elemente(self, namen):
        u"""Kennung → (Art, Vorlage, Marken, hat `name`)."""
        gefunden = {}
        for name in namen:
            text = io.open(self.vorlagen / name, encoding='utf-8').read()
            for art, vorn, kennung, hinten in ELEMENT.findall(text):
                # `{{ kennung }}` ist eine Vorlagenvariable, keine Kennung.
                if ANZEIGE.search(kennung) or '{' in kennung:
                    continue
                merkmale = vorn + hinten
                marken = []
                for klassen in re.findall(r'class="([^"]*)"', merkmale):
                    marken.extend(klassen.split())
                marken.extend('data-' + n for n in
                              re.findall(r'\bdata-([\w-]+)=', merkmale))
                hatname = bool(re.search(r'\bname="[^"]+"', merkmale))
                gefunden.setdefault(kennung,
                                    (art.lower(), name, marken, hatname))
        return gefunden

    def code(self, namen=()):
        if self._code is None:
            self._code = '\n'.join(
                io.open(pfad, encoding='utf-8', errors='replace').read()
                for pfad in self.statik.rglob('*.js')
                if not any(teil in pfad.parts for teil in FREMD))
        # Inline-Skripte der Seite gehören dazu: Ein dort verdrahteter Knopf
        # wäre sonst ein Fehlalarm.
        teile = [self._code]
        for name in namen:
            text = io.open(self.vorlagen / name, encoding='utf-8').read()
            teile.extend(re.findall(r'<script[^>]*>(.*?)</script>', text, re.S))
        return '\n'.join(teile)

    # ------------------------------------------------------------- Urteil

    @staticmethod
    def verzeichnis(code):
        u"""Den Code EINMAL zerlegen statt je Kennung zu durchsuchen.

        Gemessen am 09.09.2026: Ein Regex-Lauf über die 4,0 MB Skriptcode
        kostet Millisekunden, aber 184 Kennungen mal mehrere Muster ergaben
        1,42 s allein für die Szene-Seite — der Test wäre damit ein Fall für
        `core/tests/longrunner/` gewesen. Mit dem Verzeichnis sind es 0,01 s.
        """
        literale = set()
        suffixe = set()
        praefixe = set()
        for text in re.findall(r"'([^'\n]{2,80})'|\"([^\"\n]{2,80})\"|`([^`\n]{2,80})`",
                               code):
            wert = text[0] or text[1] or text[2]
            if '${' in wert:
                # `${vorsilbe}-roughness` -> Suffix; `prop-region-${rid}` ->
                # Präfix. Beides zugleich ist möglich.
                kopf = wert.partition('${')[0]
                if kopf:
                    praefixe.add(kopf.rstrip('-'))
                hinten = wert.rsplit('}', 1)[-1]
                if hinten:
                    suffixe.add(hinten.lstrip('-'))
                continue
            literale.add(wert)
            if wert.endswith('-'):
                praefixe.add(wert.rstrip('-'))
        return literale, suffixe, praefixe

    @staticmethod
    def erwaehnt(kennung, verzeichnis, code):
        u"""Wie die Kennung im Code vorkommt — oder `None`."""
        literale, suffixe, praefixe = verzeichnis
        if kennung in literale:
            return 'woertlich'
        teile = kennung.split('-')
        for ab in range(1, len(teile)):
            if '-'.join(teile[ab:]) in suffixe:
                return 'zusammengesetzt'
        for bis in range(len(teile) - 1, 0, -1):
            if '-'.join(teile[:bis]) in praefixe:
                return 'angehaengt'
        if kennung in code:
            return 'im Text'
        return None

    @staticmethod
    def ueber_marke(marken, waehler):
        u"""Greift ein Skript das Element über Klasse oder data-Attribut?

        `hb-`-Klassen bleiben draussen: Das sind Stilhelfer (`hb-dehnt`), die
        nichts über Bedienung sagen.
        """
        for marke in marken:
            if marke and not marke.startswith('hb-') and marke in waehler:
                return True
        return False

    @staticmethod
    def waehler(code):
        u"""Klassen und data-Namen, über die Skripte Elemente greifen."""
        gefunden = set()
        for treffer in re.findall(r'[.\[]([A-Za-z][\w-]{2,60})', code):
            gefunden.add(treffer)
        return gefunden

    def _grundindex(self):
        u"""Verzeichnis und Wähler des GEMEINSAMEN Codes — einmal je Lauf.

        Ohne diesen Zwischenspeicher lief die Zerlegung der 4,0 MB je Seite
        erneut: 3,3 s für zwanzig Seiten statt 0,4 s. Die Inline-Skripte der
        einzelnen Seite kommen danach dazu, die sind klein.
        """
        if getattr(self, '_index', None) is None:
            code = self.code()
            self._index = (Bedienelemente.verzeichnis(code),
                           Bedienelemente.waehler(code))
        return self._index

    def ohne_hoerer(self, seite):
        u"""Die Kennungen dieser Seite, die kein Skript anfasst."""
        namen = self.kette(seite)
        code = self.code(namen)
        (literale, suffixe, praefixe), waehler = self._grundindex()
        inline = '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>',
                                      '\n'.join(io.open(self.vorlagen / n,
                                                        encoding='utf-8').read()
                                                for n in namen), re.S))
        if inline.strip():
            zusatz = Bedienelemente.verzeichnis(inline)
            literale = literale | zusatz[0]
            suffixe = suffixe | zusatz[1]
            praefixe = praefixe | zusatz[2]
            waehler = waehler | Bedienelemente.waehler(inline)
        verzeichnis = (literale, suffixe, praefixe)
        stumm = []
        for kennung, (art, vorlage, marken, hatname) in \
                sorted(self.elemente(namen).items()):
            if hatname or Bedienelemente.ueber_marke(marken, waehler):
                continue
            if Bedienelemente.erwaehnt(kennung, verzeichnis, code) \
                    in (None, 'im Text'):
                stumm.append((kennung, art, vorlage))
        return stumm
