# -*- coding: utf-8 -*-
"""Recherchemodelletabelle — die Modelle als Struktur für `djangobase/_tabelle.html` (10.10.2026).

Spalten (Edgar: „Links, Vorschau (Icon), Auflösung, Größe, Dateityp, Download-Link"): Vorschau, Modell, Quelle, Auflösung, Größe, Dateityp, Download, Lizenz.
Alles aus der JSON-Datei gilt als nicht vertrauenswürdig (Texte von Fremdseiten): jeder Text wird maskiert, jede Adresse muss mit `https://` beginnen
(sonst steht dort kein Link und kein Bild), ein Bild nur als lokale Vorschau `recherche/modelle_internet/<name>.webp|png|jpg`.

Auflösung und Größe tragen den Rohwert als `data-sort` (Dreiecke bzw. MB): die Sortierung des Browsers liest sonst die Anzeige, und „1.967,9 MB“ wäre kleiner als „380,2 MB“.
"""

import re

from django.utils.html import escape

__all__ = ['Recherchemodelletabelle']


class Recherchemodelletabelle:
    LOKAL = re.compile(r'^recherche/modelle_internet/[A-Za-z0-9._-]+\.(?:webp|png|jpe?g)$')
    #: Beleg → Beschriftung der kleinen Marke und ihr Hinweis.
    BELEGE = {
        'gemessen': ('gemessen', 'Am 10.10.2026 selbst gemessen (Serverantwort, Dateiverzeichnis oder geladene Probe)'),
        'angabe': ('Angabe', 'Angabe des Anbieters oder der Datensatzkarte — nicht nachgeprüft'),
        'vermutung': ('Vermutung', 'Eigene Einschätzung oder Idee — nicht geprüft'),
    }
    #: Die Urteile der Bewertung, bester zuerst: Schlüssel in der Datei → Beschriftung der Marke.
    URTEILE = {'empfohlen': 'Empfohlen', 'bedingt': 'Bedingt', 'nicht_passend': 'Nicht passend'}
    #: (Schlüssel, Kopf, Hinweis, rechtsbündig, sortiert nicht)
    SPALTEN = (
        ('bild', 'Vorschau', 'Ein Klick zeigt das Bild groß', False, True),
        ('name', 'Modell', 'Name, kurze Beschreibung, Hinweise', False, False),
        ('bewertung', 'Bewertung', 'Einschätzung für 3dTools; sortiert nach dem Rang (1 = am besten)', False, False),
        ('quelle', 'Quelle', 'Seite des Anbieters', False, False),
        ('aufloesung', 'Auflösung', 'Sortiert nach der höchsten genannten Dreieckszahl', False, False),
        ('groesse', 'Größe', 'Sortiert nach dem größten genannten Paket (MB)', False, False),
        ('dateityp', 'Dateityp', '', False, False),
        ('download', 'Download', 'Direkte Adressen; die Größe steht dahinter', False, True),
        ('lizenz', 'Lizenz', '', False, False),
    )

    @staticmethod
    def https(adresse):
        """Die Adresse, wenn sie mit `https://` beginnt, sonst leer — fremde Adressen nie ungeprüft in href/src."""
        return adresse if isinstance(adresse, str) and adresse.startswith('https://') else ''

    @classmethod
    def bildadresse(cls, wert):
        """`/static/…` für eine lokale Vorschau der Ablage; alles andere (auch `..`) ist leer."""
        return '/static/' + wert if isinstance(wert, str) and cls.LOKAL.match(wert) else ''

    @classmethod
    def _link(cls, text, adresse, klasse=''):
        ziel = cls.https(adresse)
        if not ziel:
            return escape(text)
        art = f' class="{klasse}"' if klasse else ''
        return f'<a{art} href="{escape(ziel)}" target="_blank" rel="noopener noreferrer">{escape(text)}</a>'

    @classmethod
    def _marke(cls, beleg):
        text, titel = cls.BELEGE.get(beleg, ('?', 'Beleg unbekannt'))
        return f'<span class="mi-beleg mi-beleg-{escape(beleg)}" title="{escape(titel)}">{escape(text)}</span>'

    @classmethod
    def _zeilen(cls, block):
        """Die Zeilen einer Zelle (Auflösung, Größe) als Liste, jede mit ihrer Marke."""
        punkte = ''.join(f'<li>{escape(z["text"])} {cls._marke(z["beleg"])}</li>' for z in block['zeilen'])
        return f'<ul class="mi-liste">{punkte}</ul>'

    @classmethod
    def _bewertung(cls, m):
        """Marke (Urteil) und Rang, die Gründe mit ihrem Beleg und der nächste Schritt."""
        b = m['bewertung']
        beschriftung = cls.URTEILE.get(b['urteil'], b['urteil'])
        kopf = (f'<span class="mi-urteil mi-urteil-{escape(b["urteil"])}">{escape(beschriftung)}</span> '
                f'<span class="mi-rang" title="Rang unter den Funden dieser Seite (1 = am besten)">Rang {int(b["rang"])}</span>')
        schritt = f'<div class="mi-schritt"><b>Nächster Schritt:</b> {escape(b["naechster_schritt"])}</div>' if b.get('naechster_schritt') else ''
        return kopf + cls._zeilen(b) + schritt

    @classmethod
    def _bild(cls, m):
        adresse = cls.bildadresse(m.get('bild'))
        if not adresse:
            return '<span class="mi-fehlt">–</span>'
        titel = f'Vorschau: {m["bild_herkunft"]}'
        return (f'<img class="mi-bild" loading="lazy" referrerpolicy="no-referrer" alt="{escape(m["name"])}" title="{escape(titel)}" '
                f'src="{escape(adresse)}" width="100" height="100">')

    @classmethod
    def _name(cls, m):
        hinweis = f'<div class="mi-hinweis">{escape(m["hinweis"])}</div>' if m.get('hinweis') else ''
        return f'<strong class="mi-name">{escape(m["name"])}</strong><div class="mi-kurz">{escape(m["kurz"])}</div>{hinweis}'

    @classmethod
    def _downloads(cls, m):
        punkte = ''.join(
            f'<li>{cls._link(d["label"], d["url"])} <span class="mi-klein">{escape(d["groesse"])}</span></li>' for d in m['downloads'])
        return f'<ul class="mi-liste mi-downloads">{punkte}</ul>'

    @classmethod
    def _zellen(cls, m):
        quellen = '<ul class="mi-liste">' + ''.join(f'<li>{cls._link(q["label"], q["url"])}</li>' for q in m['quellen']) + '</ul>'
        return {
            'bild': {'html': cls._bild(m), 'klasse': 'mi-bildzelle'},
            'name': {'html': cls._name(m), 'sort': m['name'].lower()},
            'bewertung': {'html': cls._bewertung(m), 'sort': int(m['bewertung']['rang']), 'klasse': 'mi-bewertungszelle'},
            'quelle': {'html': quellen, 'sort': m['quellen'][0]['label'].lower()},
            'aufloesung': {'html': cls._zeilen(m['aufloesung']), 'sort': int(m['aufloesung']['sort'])},
            'groesse': {'html': cls._zeilen(m['groesse']), 'sort': float(m['groesse']['sort_mb'])},
            'dateityp': {'html': escape(m['dateityp']), 'sort': m['dateityp'].lower()},
            'download': {'html': cls._downloads(m)},
            'lizenz': {'html': escape(m['lizenz']) + (f'<div class="mi-klein">{cls._link("Lizenztext", m["lizenz_url"])}</div>' if cls.https(m.get('lizenz_url')) else ''),
                        'sort': m['lizenz'].lower()},
        }

    @classmethod
    def kopf(cls):
        return [{'label': kopf, 'key': key, 'titel': titel, 'sortAus': aus} for key, kopf, titel, _, aus in cls.SPALTEN]

    @classmethod
    def bauen(cls, modelle):
        """Die Tabelle für `djangobase/_tabelle.html`; Zeilen nach Spaltenschlüssel, nie nach Index."""
        zeilen = []
        for m in modelle:
            zellen = cls._zellen(m)
            zeilen.append({'id': m['id'], 'zellen': [zellen[key] for key, *_ in cls.SPALTEN]})
        return {'key': 'hilfe-recherche-modelle-internet', 'spalten': cls.kopf(), 'zeilen': zeilen, 'klasse': 'mi-tabelle',
                'leer': 'Noch keine Modelle erfasst — core/daten/recherche_modelle_internet.json fehlt oder ist leer.'}
