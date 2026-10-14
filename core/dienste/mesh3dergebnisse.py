# -*- coding: utf-8 -*-
"""Mesh3dergebnisse — was ein Import ergeben hat, für die Karten der Jobseite „Mesh-3D“ zusammengefasst (11.10.2026).

Liest NUR `stand.json` und die Ablage eines Imports (`Blendimportablage`) und den Auftrag „Mesh to 3D“ seines Schritts „figur“ — es
rechnet nichts. Jede Methode liefert ein kleines Wörterbuch für EINE Karte; fehlt ein Ergebnis, `None`, und die Karte bleibt leer.
Bilder gehen als Adresse über `Mesh3dendpunkte.datei` hinaus (Ordner `ergebnis`, `arbeit` oder `figur` = Ergebnisordner des Auftrags
„Mesh to 3D“), mit dem Stand der Datei als `?v=`.
"""

from django.urls import reverse

from ..daten.blendimportablage import Blendimportablage
from ..daten.meshfigurablage import Meshfigurablage

__all__ = ['Mesh3dergebnisse']


class Mesh3dergebnisse:
    #: Bilder des Auftrags „Mesh to 3D“, die als Vorschau der Figur dienen (Ordner `figur`).
    FIGURBILDER = (('vorlage', 'vorlage.png', 'Körpernetz'), ('vorn', 'vorschau_vorn.png', 'Figur vorn'),
                   ('seite', 'vorschau_seite.png', 'Figur seitlich'), ('hinten', 'vorschau_hinten.png', 'Figur hinten'),
                   ('kopf', 'vorschau_kopf.png', 'Kopf'), ('vergleich', 'vergleich.jpg', 'Vergleich Netz · Figur'))

    def __init__(self, stand):
        self.stand = stand
        self.kennung = stand.get('kennung')
        self.ergebnis = stand.get('ergebnis') or {}
        self.ablage = Blendimportablage(self.kennung)
        self._uebernommene_variante()

    def _uebernommene_variante(self):
        """Hat der Nutzer eine Variante übernommen (`Mesh3dvarianten.uebernehmen`), zeigt die Seite ihre Figur und ihr Modell statt der des ersten Laufs. Rechnet der Import gerade, gilt der Stand, wie er ist."""
        if self.stand.get('bereich') != 'mesh3d' or self.stand.get('status') == 'laeuft':
            return
        from .mesh3dvarianten import Mesh3dvarianten

        job = Mesh3dvarianten.haupt_job(self.kennung)
        if job is None:
            return
        ergebnis = dict(self.ergebnis)
        ergebnis['figur'] = Mesh3dvarianten.figur_von(job)
        if job.modell:
            ergebnis['modell'] = {'name': job.modell, 'weg': 'netz'}
        self.ergebnis = ergebnis

    # ---------------------------------------------------------------- Adressen

    def adresse(self, ordner, name):
        """Adresse einer Bilddatei oder `None`, wenn es sie (noch) nicht gibt."""
        pfad = self.pfad(ordner, name)
        if pfad is None or not pfad.is_file():
            return None
        return '%s?v=%d' % (reverse('mesh3d_datei', args=[self.kennung, ordner, name]), int(pfad.stat().st_mtime))

    def pfad(self, ordner, name):
        if ordner == 'ergebnis':
            return self.ablage.ergebnis(name)
        if ordner == 'arbeit':
            return self.ablage.arbeit(name)
        if ordner == 'pose':
            return self.ablage.arbeit('pose') / name
        if ordner == 'segmentierung':
            return self.ablage.arbeit('segmentierung') / name
        if ordner == 'figur':
            figur = (self.ergebnis.get('figur') or {}).get('kennung')
            return Meshfigurablage(figur).ergebnis(name) if figur else None
        return None

    # ---------------------------------------------------------------- Karten

    def rollen(self):
        """Die Netze der Datei mit ihrer Rolle — Tabelle der Karte „Netze und Rollen“."""
        zeilen = [{'name': r.get('name'), 'rolle': r.get('rolle'), 'art': r.get('art') or r.get('ordner') or '',
                   'punkte': r.get('punkte')} for r in self.stand.get('rollen') or []]
        export = self.ergebnis.get('export') or {}
        return {'netze': export.get('netze', len(zeilen)), 'zeilen': zeilen, 'koerper': export.get('koerper')} if zeilen else None

    def umposen(self):
        e = self.ergebnis.get('umposen')
        if not isinstance(e, dict):
            return None
        segmente = e.get('segmente') or []
        gedreht = [s for s in segmente if s.get('drehung_grad') is not None]
        return {'aus': bool(e.get('aus')), 'grund': e.get('grund'), 'segmente': len(segmente), 'gedreht': len(gedreht)}

    def pose(self):
        """Schritt „Pose“ (SAM 3D Body) — gesetzt, sobald der Schritt gerechnet hat."""
        e = self.ergebnis.get('pose')
        if not isinstance(e, dict):
            return None
        bilder = {n: self.adresse('pose', d) for n, d in (e.get('bilder') or {}).items()}
        return {**{k: v for k, v in e.items() if k != 'bilder'}, 'bilder': {n: a for n, a in bilder.items() if a}}

    def segmentierung(self):
        """Schritt „Segmentierung“ (Weg „netz“, `Blendimportsegmentierung`): Optionen, je Ansicht IoU, gesehene Flächen und Anteile mit Rendering und Überlagerung, die Kennzahlen; dazu, was „Mesh to 3D“
        davon übernommen hat (`ergebnis.figur.kleidung.sapiens`, Hautton) — die Karte zeigt es als Zahl, nicht als Behauptung."""
        e = self.ergebnis.get('segmentierung')
        if not isinstance(e, dict):
            return None
        ansichten = [{**{k: a.get(k) for k in ('rolle', 'iou', 'sichtbar', 'anteile', 'haarfarbe')},
                      'rendering': self.adresse('segmentierung', '%s.png' % a.get('rolle')),
                      'ueberlagerung': self.adresse('segmentierung', a['ueberlagerung']) if a.get('ueberlagerung') else None} for a in e.get('ansichten') or []]
        return {'optionen': e.get('optionen'), 'ansichten': ansichten, 'kennzahlen': e.get('kennzahlen')}

    def koerper(self):
        e = self.ergebnis.get('koerper')
        return {k: e.get(k) for k in ('punkte', 'dreiecke', 'augen', 'atlas', 'ergaenzt', 'weg', 'hoehe_m_original', 'hoehe_m', 'faktor', 'groesse_mb', 'bilder')} if isinstance(e, dict) else None

    def figur(self):
        e = self.ergebnis.get('figur')
        if not isinstance(e, dict) or not e.get('kennung'):
            return None
        bilder = [{'schluessel': s, 'titel': t, 'adresse': self.adresse('figur', d)} for s, d, t in self.FIGURBILDER]
        mess = e.get('schammessung') if isinstance(e.get('schammessung'), dict) else None
        return {'id': e.get('id'), 'kennung': e['kennung'], 'fehlt': self._auftrag_fehlt(e.get('id')), 'regler': e.get('regler'), 'rest': e.get('rest'),
                'hautmodell': e.get('hautmodell'), 'kleidung': e.get('kleidung'),
                'schammessung': {'urteil': mess.get('urteil'), 'abweichungen': mess.get('abweichungen')} if mess else None,
                'bilder': [b for b in bilder if b['adresse']], **self._figurlauf()}

    @staticmethod
    def _auftrag_fehlt(figur_id):
        """Nennt der Stand einen Auftrag „Mesh to 3D“, den es nicht mehr gibt? (Gemessen 13.10.2026: eine Kopie nannte den Auftrag ihres gelöschten Originals — die Bühne bekam 404.)"""
        from ..models import Meshfigurauftrag

        try:
            return bool(figur_id) and not Meshfigurauftrag.objects.filter(pk=figur_id).exists()
        except (ValueError, TypeError):                     # keine gültige UUID im Stand
            return True

    def _figurlauf(self):
        """Läuft der Schritt „figur“ gerade: Fortschritt des Auftrags „Mesh to 3D“ (Schritt, Prozent)."""
        from ..models import Meshfigurauftrag
        from .blendimportlauf import Blendimportlauf

        kennung = (self.ergebnis.get('figur') or {}).get('kennung')
        if self.stand.get('schritt') != 'figur' or self.stand.get('status') != 'laeuft' or not kennung:
            return {}
        job = Meshfigurauftrag.objects.filter(kennung=kennung).first()
        if job is None:
            return {}
        von, bis = Blendimportlauf.baender_fuer(self.stand.get('weg'))['figur']   # der Weg „netz“ hat andere Bänder als „teile“ (Zauberer: 16 %, nicht 9 %)
        return {'lauf': {'schritt': job.schritt, 'prozent': job.progress, 'detail': job.progress_detail,
                         'fortschritt': int(von + (bis - von) * (job.progress or 0) / 100.0)}}

    def finger(self):
        e = self.ergebnis.get('finger')
        return e if isinstance(e, dict) else None

    def stuecke(self):
        """Eine Zeile je Stück: Rolle, Name in der Garderobe, Kategorie, Abnahme (Haltungstreue, Kanten)."""
        e = self.ergebnis.get('stuecke')
        if not isinstance(e, dict):
            return None
        bericht = e.get('bericht') or {}
        zeilen = []
        for schluessel, kennung in (e.get('stuecke') or {}).items():
            b = bericht.get(schluessel) if isinstance(bericht.get(schluessel), dict) else {}
            p = b.get('pruefung') if isinstance(b.get('pruefung'), dict) else {}
            zeilen.append({'schluessel': schluessel, 'kennung': kennung, 'name': b.get('name') or kennung, 'kategorie': self._kategorie(b.get('kategorie')),
                           'punkte': b.get('punkte'), 'haut_median_mm': b.get('haut_median_mm'), 'rest_max_mm': b.get('rest_max_mm'),
                           'warnungen': p.get('warnungen') or [], 'befund': p.get('befund')})
        gescheitert = [{'schluessel': s, 'fehler': b.get('fehler')} for s, b in bericht.items() if isinstance(b, dict) and b.get('fehler')]
        aus = [{'schluessel': s, 'grund': b.get('aus')} for s, b in bericht.items() if isinstance(b, dict) and b.get('aus')]
        return {'aus': bool(e.get('aus')), 'zeilen': zeilen, 'gescheitert': gescheitert, 'ohne': aus,
                'bogen': self.adresse('ergebnis', 'stuecke_bogen.png')}

    @staticmethod
    def _kategorie(wert):
        """Die Kategorie der Garderobe als kurzer Text: aus `['Follower/Wardrobe/Footwear', …]` wird „Footwear“."""
        erste = wert[0] if isinstance(wert, (list, tuple)) and wert else wert
        return str(erste).rstrip('/').split('/')[-1] if erste else ''

    def haut(self):
        e = self.ergebnis.get('haut')
        if not isinstance(e, dict):
            return None
        kacheln = e.get('kacheln') or {}
        nummern = sorted({str(k).split(':')[0] for k in kacheln})
        return {'abstand': e.get('abstand'), 'deckung': e.get('deckung'), 'normalen_flach': e.get('normalen_flach'),
                'kacheln': [{'nummer': n, 'farbe': self.adresse('ergebnis', kacheln.get(n))} for n in nummern if kacheln.get(n)]}

    def augen(self):
        e = self.ergebnis.get('augen')
        if not isinstance(e, dict):
            return None
        return {'art': e.get('art'), 'bild': self.adresse('ergebnis', e.get('datei')) if e.get('datei') else None}

    def modell(self):
        e = self.ergebnis.get('modell')
        return {'name': e.get('name'), 'daz': e.get('daz'), 'weg': e.get('weg')} if isinstance(e, dict) else None
