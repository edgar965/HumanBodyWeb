# -*- coding: utf-8 -*-
"""Recherchetabelle — die Projekte der Recherche als Struktur für `djangobase/_tabelle.html` (04.10.2026).

Spalten (Edgar): Name, Prio (Handeingabe, `Rechercheprio`), Kategorie (sortierbar; Edgar, 06.10.2026: „sortierbare Spalte Kategorie … wo ist die Spalte??“ — bis dahin stand sie nur als kleine Zeile unter dem Namen), Kurzbeschreibung, GitHub-Link, Hugging Face (Demo/Modell/Daten), Hauptbild, Sterne bei GitHub, letzte Aktualisierung, Beschreibung, Details, ToDo. Alles, was aus der JSON-Datei kommt, stammt aus fremden
READMEs und gilt als nicht vertrauenswürdig: jeder Text wird maskiert, jede Adresse muss mit `https://` beginnen (sonst steht dort kein Link und kein Bild).

Sterne und Datum tragen den Rohwert als `data-sort` (die Sortierung des Browsers liest sonst die Anzeige: „12.345" wäre kleiner als „9.100"); Bild- und ToDo-Spalte sortieren nicht bzw. nach Text.
"""

import re
from datetime import date

from django.utils.html import escape

from .rechercheprio import Rechercheprio

__all__ = ['Recherchetabelle']


class Recherchetabelle:
    KEY = 'hilfe-recherche-human3d'
    #: Die Ablage der lokalen Vorschaubilder: `HumanBodyWeb/static/recherche/human3d/` (WebP, vom Wegwerfskript `bilder_lokal.py` erzeugt).
    LOKAL = re.compile(r'^recherche/human3d/[A-Za-z0-9._-]+\.(?:webp|png|jpe?g)$')

    SPALTEN = (
        ('Name', 'name', False, False, 'Name des Projekts'),
        ('Prio', 'prio', True, False, 'Deine Reihenfolge: ob wir das testen oder einbauen (1 = zuerst). Jede Zahl nur einmal — eine vergebene Zahl schiebt die anderen nach hinten'),
        ('Kategorie', 'kategorie', False, False, 'Kategorie des Projekts (die Liste darüber zählt sie) — ein Klick auf den Spaltenkopf sortiert danach'),
        ('Kurzbeschreibung', 'kurz', False, False, 'Ein Satz: was das Projekt tut'),
        ('GitHub', 'github', False, False, 'Repository auf GitHub (öffnet in neuem Tab)'),
        ('Hugging Face', 'hf', False, False, 'Demo (Space), Modell und Datensatz des Projekts bei Hugging Face — aus dem README, über die HF-Schnittstelle geprüft; Likes im Hinweis'),
        ('Hauptbild', 'bild', False, True, 'Ein aussagekräftiges Bild aus dem Projekt (verkleinerte lokale Kopie) — ein Klick öffnet es groß'),
        ('Sterne bei GitHub', 'sterne', True, False, 'Sterne laut GitHub-Abfrage am Stand der Seite'),
        ('Letzte Aktualisierung', 'aktualisiert', False, False, 'Letzter Push ins Repository (GitHub „pushed_at")'),
        ('Beschreibung', 'beschreibung', False, False, 'Was es tut und wie'),
        ('Details', 'details', False, True, 'Eingabe, Ausgabe, Modelle, Lizenz, Besonderheiten'),
        ('ToDo', 'todo', False, False, 'Was wir im Projekt nicht haben — Klick öffnet ein Fenster mit mehr Infos und Bildern'),
    )

    @staticmethod
    def https(adresse):
        """Die Adresse, wenn sie mit `https://` beginnt, sonst leer — fremde Adressen nie ungeprüft in href/src."""
        return adresse if isinstance(adresse, str) and adresse.startswith('https://') else ''

    @staticmethod
    def datum(iso):
        try:
            return date.fromisoformat(str(iso)[:10]).strftime('%d.%m.%Y')
        except ValueError:
            return str(iso or '–')

    @staticmethod
    def zahl(n):
        return f'{int(n or 0):,}'.replace(',', '.')

    @classmethod
    def bildadresse(cls, wert):
        """Die Adresse eines Bildes für `src`: eine lokale Vorschau (`recherche/human3d/<name>.webp` → `/static/…`) oder, wenn es noch keine gibt, eine https-Adresse; sonst leer.
        Der lokale Pfad muss genau der Form der Ablage entsprechen — in der JSON-Datei steht fremd erzeugter Inhalt, kein Pfad mit `..` darf je als Adresse herauskommen."""
        if isinstance(wert, str) and cls.LOKAL.match(wert):
            return '/static/' + wert
        return cls.https(wert)

    @classmethod
    def _bild(cls, p):
        adresse = cls.bildadresse(p.get('bild'))
        if not adresse:
            return '<span class="rc-fehlt">–</span>'
        return (f'<img class="rc-bild" loading="lazy" referrerpolicy="no-referrer" alt="{escape(p["name"])}" '
                f'src="{escape(adresse)}" width="150" height="100">')

    #: Hugging Face: Art → (Beschriftung, Adresspräfix). Die Adresse baut IMMER der Server aus der geprüften Kennung — nie eine Adresse aus der Datei.
    HF_ARTEN = {'space': ('Demo', 'https://huggingface.co/spaces/'), 'model': ('Modell', 'https://huggingface.co/'), 'dataset': ('Daten', 'https://huggingface.co/datasets/')}
    HF_KENNUNG = re.compile(r'^[A-Za-z0-9][\w.-]*/[A-Za-z0-9][\w.-]*$')

    @classmethod
    def hf_liste(cls, p):
        """Die gültigen Hugging-Face-Einträge `{typ, id, likes, label, url}` eines Projekts (unbekannte Art oder Kennung wird verworfen)."""
        ergebnis = []
        for h in p.get('hf') or []:
            art = cls.HF_ARTEN.get(h.get('typ'))
            kennung = h.get('id')
            if art and isinstance(kennung, str) and cls.HF_KENNUNG.match(kennung):
                ergebnis.append({'typ': h['typ'], 'id': kennung, 'likes': int(h.get('likes') or 0), 'label': art[0], 'url': art[1] + kennung})
        return ergebnis

    @classmethod
    def hf_rang(cls, p):
        """`data-sort` der Spalte: Demo zählt am meisten, dann Modell, dann Datensatz (4/2/1 addiert); ohne Eintrag 0."""
        arten = {h['typ'] for h in cls.hf_liste(p)}
        return (4 if 'space' in arten else 0) + (2 if 'model' in arten else 0) + (1 if 'dataset' in arten else 0)

    @classmethod
    def _hf(cls, p):
        liste = cls.hf_liste(p)
        if not liste:
            return '<span class="rc-fehlt">–</span>'
        je_art = {}
        teile = []
        for h in liste:
            je_art[h['typ']] = je_art.get(h['typ'], 0) + 1
            nummer = f' {je_art[h["typ"]]}' if sum(1 for x in liste if x['typ'] == h['typ']) > 1 else ''
            titel = f'{h["id"]} — ♥ {h["likes"]}'
            teile.append(f'<a class="rc-hf rc-hf-{h["typ"]}" href="{escape(h["url"])}" target="_blank" rel="noopener noreferrer" title="{escape(titel)}">{escape(h["label"])}{nummer}</a>')
        return '<div class="rc-hf-liste">' + ''.join(teile) + '</div>'

    @staticmethod
    def _fork(p):
        """Die Zeile „Fork von …" unter dem Namen (nur bei Forks; Edgar: „inkludiere auch Forks, falls die was Besseres haben" — `fork_grund` sagt, was besser ist)."""
        if not p.get('fork_von'):
            return ''
        grund = f' — {escape(p["fork_grund"])}' if p.get('fork_grund') else ''
        return f'<div class="rc-fork" title="Dieses Projekt ist ein Fork">Fork von {escape(p["fork_von"])}{grund}</div>'

    @classmethod
    def _prio(cls, p, prio):
        """Das Zahlenfeld der Spalte „Prio" (leer = nicht eingestuft); `data-vorher` hält den gespeicherten Stand, auf den ein gescheitertes Speichern zurückspringt."""
        titel = f'Prio für {p["name"]}'
        klasse = 'rc-prio rc-prio-gesetzt' if prio else 'rc-prio'
        return (f'<input type="number" class="{klasse}" min="1" max="{Rechercheprio.HOECHSTENS}" step="1" inputmode="numeric" data-id="{escape(p["id"])}" '
                f'data-vorher="{prio or ""}" value="{prio or ""}" aria-label="{escape(titel)}" title="{escape(titel)} — leer lassen = keine Prio">')

    @classmethod
    def _zeile(cls, p, prio=None):
        github = cls.https(p.get('url'))
        link = (f'<a href="{escape(github)}" target="_blank" rel="noopener noreferrer">{escape(p["repo"])}</a>'
                if github else escape(p['repo']))
        details = '<ul class="rc-liste">' + ''.join(f'<li>{escape(d)}</li>' for d in p['details']) + '</ul>'
        todo = (f'<button type="button" class="rc-todo" data-id="{escape(p["id"])}" title="Mehr Infos und Bilder">'
                f'{escape(p["todo_kurz"])} <span class="rc-mehr">mehr …</span></button>')
        return {'id': p['id'], 'zellen': [
            {'html': f'<strong class="rc-name">{escape(p["name"])}</strong>{cls._fork(p)}', 'sort': p['name'].lower()},
            {'html': cls._prio(p, prio), 'sort': prio or Rechercheprio.SORT_OHNE_PRIO, 'klasse': 'rc-priozelle'},
            {'html': escape(p['kategorie']), 'sort': p['kategorie'].lower(), 'klasse': 'rc-kategoriezelle'},
            {'html': escape(p['kurz'])},
            {'html': link, 'sort': p['repo'].lower()},
            {'html': cls._hf(p), 'sort': cls.hf_rang(p), 'klasse': 'rc-hfzelle'},
            {'html': cls._bild(p), 'klasse': 'rc-bildzelle'},
            {'html': cls.zahl(p['sterne']), 'sort': int(p['sterne']), 'klasse': 'num'},
            {'html': cls.datum(p['aktualisiert']), 'sort': str(p['aktualisiert'])[:10]},
            {'html': escape(p['beschreibung'])},
            {'html': details},
            {'html': todo, 'klasse': 'rc-todozelle', 'sort': p['todo_kurz'].lower()},
        ]}

    @classmethod
    def bauen(cls, projekte, prios=None):
        """`prios` = `{projektkennung: Prio}` (`Rechercheprio.laden()`); ohne Angabe ist niemand eingestuft."""
        prios = prios or {}
        kopf = [{'label': label, 'key': key, 'num': num, 'sortAus': aus, 'titel': titel} for label, key, num, aus, titel in cls.SPALTEN]
        return {'key': cls.KEY, 'spalten': kopf, 'zeilen': [cls._zeile(p, prios.get(p['id'])) for p in projekte], 'klasse': 'rc-tabelle',
                'leer': 'Noch keine Projekte erfasst — die Datei core/daten/recherche_human3d.json fehlt oder ist leer.'}

    @classmethod
    def popup(cls, projekte):
        """Die Felder, die das Fenster nach einem Klick auf ToDo zeigt — als JSON an die Seite, je Projekt unter seiner `id`."""
        felder = ('name', 'repo', 'kategorie', 'kurz', 'beschreibung', 'details', 'todo_kurz', 'todo', 'sprache', 'lizenz', 'sterne', 'angelegt', 'aktualisiert')
        aus = {}
        for p in projekte:
            eintrag = {f: p.get(f) for f in felder}
            eintrag['url'] = cls.https(p.get('url'))
            bilder = [(cls.bildadresse(x), cls.https(q)) for x, q in zip([p.get('bild')] + list(p.get('bilder') or []), [p.get('bild_quelle')] + list(p.get('bilder_quellen') or []) + [None] * 8)]
            bilder = [(adresse, quelle) for adresse, quelle in bilder if adresse]
            # Bild und Galerie getrennt, dazu je Bild die Quelle (Original beim Projekt) — das Fenster verlinkt darauf; ohne Quelle leer.
            eintrag['bild'] = bilder[0][0] if bilder and cls.bildadresse(p.get('bild')) else ''
            eintrag['bilder'] = [a for a, _ in (bilder[1:] if eintrag['bild'] else bilder)]
            eintrag['quellen'] = [q for _, q in bilder]
            eintrag['fork_von'] = p.get('fork_von') or ''
            eintrag['fork_grund'] = p.get('fork_grund') or ''
            eintrag['hf'] = cls.hf_liste(p)
            aus[p['id']] = eintrag
        return aus
