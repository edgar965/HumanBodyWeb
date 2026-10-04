# -*- coding: utf-8 -*-
"""Recherchetabelle — die Projekte der Recherche als Struktur für `djangobase/_tabelle.html` (04.10.2026).

Spalten (Edgar): Name, Kurzbeschreibung, GitHub-Link, Hauptbild, Sterne bei GitHub, letzte Aktualisierung, Beschreibung, Details, ToDo. Alles, was aus der JSON-Datei kommt, stammt aus fremden
READMEs und gilt als nicht vertrauenswürdig: jeder Text wird maskiert, jede Adresse muss mit `https://` beginnen (sonst steht dort kein Link und kein Bild).

Sterne und Datum tragen den Rohwert als `data-sort` (die Sortierung des Browsers liest sonst die Anzeige: „12.345" wäre kleiner als „9.100"); Bild- und ToDo-Spalte sortieren nicht bzw. nach Text.
"""

from datetime import date

from django.utils.html import escape

__all__ = ['Recherchetabelle']


class Recherchetabelle:
    KEY = 'hilfe-recherche-human3d'

    SPALTEN = (
        ('Name', 'name', False, False, 'Name des Projekts und seine Kategorie'),
        ('Kurzbeschreibung', 'kurz', False, False, 'Ein Satz: was das Projekt tut'),
        ('GitHub', 'github', False, False, 'Repository auf GitHub (öffnet in neuem Tab)'),
        ('Hauptbild', 'bild', False, True, 'Ein aussagekräftiges Bild aus dem Projekt (README), direkt von GitHub geladen'),
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
    def _bild(cls, p):
        adresse = cls.https(p.get('bild'))
        if not adresse:
            return '<span class="rc-fehlt">–</span>'
        return (f'<img class="rc-bild" loading="lazy" referrerpolicy="no-referrer" alt="{escape(p["name"])}" '
                f'src="{escape(adresse)}" width="150" height="100">')

    @classmethod
    def _zeile(cls, p):
        github = cls.https(p.get('url'))
        link = (f'<a href="{escape(github)}" target="_blank" rel="noopener noreferrer">{escape(p["repo"])}</a>'
                if github else escape(p['repo']))
        details = '<ul class="rc-liste">' + ''.join(f'<li>{escape(d)}</li>' for d in p['details']) + '</ul>'
        todo = (f'<button type="button" class="rc-todo" data-id="{escape(p["id"])}" title="Mehr Infos und Bilder">'
                f'{escape(p["todo_kurz"])} <span class="rc-mehr">mehr …</span></button>')
        return {'id': p['id'], 'zellen': [
            {'html': f'<strong class="rc-name">{escape(p["name"])}</strong><div class="rc-kategorie">{escape(p["kategorie"])}</div>', 'sort': p['name'].lower()},
            {'html': escape(p['kurz'])},
            {'html': link, 'sort': p['repo'].lower()},
            {'html': cls._bild(p), 'klasse': 'rc-bildzelle'},
            {'html': cls.zahl(p['sterne']), 'sort': int(p['sterne']), 'klasse': 'num'},
            {'html': cls.datum(p['aktualisiert']), 'sort': str(p['aktualisiert'])[:10]},
            {'html': escape(p['beschreibung'])},
            {'html': details},
            {'html': todo, 'klasse': 'rc-todozelle', 'sort': p['todo_kurz'].lower()},
        ]}

    @classmethod
    def bauen(cls, projekte):
        kopf = [{'label': label, 'key': key, 'num': num, 'sortAus': aus, 'titel': titel} for label, key, num, aus, titel in cls.SPALTEN]
        return {'key': cls.KEY, 'spalten': kopf, 'zeilen': [cls._zeile(p) for p in projekte], 'klasse': 'rc-tabelle',
                'leer': 'Noch keine Projekte erfasst — die Datei core/daten/recherche_human3d.json fehlt oder ist leer.'}

    @classmethod
    def popup(cls, projekte):
        """Die Felder, die das Fenster nach einem Klick auf ToDo zeigt — als JSON an die Seite, je Projekt unter seiner `id`."""
        felder = ('name', 'repo', 'kategorie', 'kurz', 'beschreibung', 'details', 'todo_kurz', 'todo', 'sprache', 'lizenz', 'sterne', 'angelegt', 'aktualisiert')
        aus = {}
        for p in projekte:
            eintrag = {f: p.get(f) for f in felder}
            eintrag['url'] = cls.https(p.get('url'))
            eintrag['bild'] = cls.https(p.get('bild'))
            eintrag['bilder'] = [b for b in (cls.https(x) for x in p.get('bilder') or []) if b]
            aus[p['id']] = eintrag
        return aus
