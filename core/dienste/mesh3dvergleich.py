# -*- coding: utf-8 -*-
"""Mesh3dvergleich — Hauptausgabe und Varianten eines Imports nebeneinander, mit Empfehlung (13.10.2026).

Liefert der Jobseite (`zustand.varianten`) je Feld (`kleidung_zug`, `basis`, `pose`) eine Gruppe aus der Hauptausgabe und ihren Varianten, je Spalte die Kennzahlen aus `ergebnis.abnahme` und das Vergleichsbild.

**Die Empfehlung ist keine Note.** Es gibt keine Gesamtzahl: eine Spalte wird nur empfohlen, wenn sie in jeder Zeile des Gütemaßes (`GUETE`) mindestens so gut ist wie jede andere (Unterschiede unter der Toleranz der Zeile
gelten als gleich) und in mindestens einer Zeile deutlich besser. Sonst steht dort „keine Empfehlung — das Bild entscheidet“. Die Umfänge der Figur (Oberschenkel, Brust …) stehen als Zeilen da, zählen aber nicht mit:
ein kleinerer Umfang ist nicht „besser“ (eine Robe soll keinen Körper aufblähen, ein Mieder soll ihn aber nicht wegrechnen) — das beurteilt das Bild.

Die Toleranzen sind Setzungen aus den Streuungen, die gemessen sind: Fit-Kette ≤ 0,03 mm und Endmaß ±0,05 mm bei gleichen Eingaben an Edgar (`meshfigur.md`), die Hand-Anpassung dagegen bimodal (Polstertänzer Hand L
174 und 18 mm bei gleichen Eingaben, `mesh-3d-ohne-nacharbeit-konzept`); 3 mm an den Händen ist also zu fein für diese Streuung und ein Unterschied darunter kein Befund.
"""

import logging

from django.urls import reverse

from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter
from .mesh3dvarianten import Mesh3dvarianten

logger = logging.getLogger('core')

__all__ = ['Mesh3dvergleich']


class Mesh3dvergleich:
    #: Zeilen der Tabelle: (Schlüssel, Titel, Einheit). Wert je Spalte: Zahl oder `None`.
    ZEILEN = (
        ('figur_netz_rms_mm', 'Figur → Netz (RMS)', 'mm'), ('netz_figur_rms_mm', 'Netz → Figur (RMS)', 'mm'),
        ('stoff_im_koerper_prozent', 'Stoff im Körper (< 0 mm)', '%'), ('stoff_tief_prozent', 'Stoff tiefer als 5 mm im Körper', '%'),
        ('hand_l_mm', 'Hand L zum Netz', 'mm'), ('hand_r_mm', 'Hand R zum Netz', 'mm'),
        ('oberschenkel_cm', 'Oberschenkel (Umfang)', 'cm'), ('huefte_cm', 'Hüfte (Umfang)', 'cm'), ('taille_cm', 'Taille (Umfang)', 'cm'), ('brust_cm', 'Brust (Umfang)', 'cm'),
        ('hoehe_cm', 'Höhe', 'cm'), ('doppelt', 'Flächen in zwei Objekten', ''), ('waisen_rest', 'Erkannte Flächen in keinem Objekt', ''),
    )
    #: Das Gütemaß: Zeile → Toleranz (kleiner ist besser). Setzungen, siehe Kopf.
    GUETE = {'figur_netz_rms_mm': 0.3, 'netz_figur_rms_mm': 0.3, 'stoff_im_koerper_prozent': 1.0, 'stoff_tief_prozent': 1.0, 'hand_l_mm': 3.0, 'hand_r_mm': 3.0, 'doppelt': 0, 'waisen_rest': 100}
    #: Eine Empfehlung braucht so viele vergleichbare Zeilen.
    MIN_ZEILEN = 3

    # --------------------------------------------------------------- Zustand

    @classmethod
    def von(cls, kennung, stand):
        """`{felder, eintraege, haupt, laeuft, minuten, zeilen, gruppen, empfehlungen}` für die Jobseite — `None` beim Weg „teile“ (dort gibt es keine Varianten)."""
        if (stand.get('weg') or 'teile') != 'netz':
            return None
        daten = Mesh3dvarianten.lesen(kennung)
        from .mesh3dvariantenlauf import Mesh3dvariantenlauf

        laeuft = Mesh3dvariantenlauf.lebt(kennung)
        hauptspalte = cls._hauptspalte(stand)
        spalten = [cls._spalte(kennung, e, laeuft) for e in daten['eintraege']]
        gruppen = [cls._gruppe(f, stand, hauptspalte, [s for s in spalten if s['feld'] == f['schluessel']], daten['vorher']) for f in Mesh3dvarianten.FELDER if f['weg'] == 'netz']
        return {
            'felder': [cls._feld(f, stand, daten) for f in Mesh3dvarianten.FELDER],
            'eintraege': spalten,
            'haupt': daten['haupt'],
            'laeuft': laeuft,
            'rechnet_import': bool(Blendimportarbeiter.lebt(Blendimportablage(kennung))),
            'zeilen': [{'schluessel': s, 'titel': t, 'einheit': e, 'gewertet': s in cls.GUETE} for s, t, e in cls.ZEILEN],
            'gruppen': [g for g in gruppen if g['spalten']],
            'empfehlungen': cls.empfehlungen(stand, gruppen),
        }

    @classmethod
    def _feld(cls, f, stand, daten):
        aktuell = Mesh3dvarianten.aktuell(stand, f['schluessel'])
        vorhanden = {e['wert'] for e in daten['eintraege'] if e['feld'] == f['schluessel']} | {daten['vorher'].get(f['schluessel'])}
        offen =[w for w, _ in f['werte'] if w != aktuell and w not in vorhanden]
        return {'schluessel': f['schluessel'], 'titel': f['titel'], 'aktuell': aktuell, 'werte': [{'wert': w, 'text': t} for w, t in f['werte']],
                'offen': offen, 'minuten': Mesh3dvarianten.MINUTEN * len(offen)}

    # --------------------------------------------------------------- Spalten

    @classmethod
    def _hauptspalte(cls, stand):
        from ..models import Meshfigurauftrag

        figur = (stand.get('ergebnis') or {}).get('figur') or {}
        try:
            job = Meshfigurauftrag.objects.filter(pk=figur.get('id')).first() if figur.get('id') else None
        except (ValueError, TypeError):
            job = None
        return cls._spalte_aus_job(job, {'id': figur.get('id'), 'titel': 'Erster Lauf', 'rolle': 'haupt', 'feld': None, 'wert': None}, False)

    @classmethod
    def _spalte(cls, kennung, eintrag, worker_lebt):
        job = Mesh3dvarianten._job(eintrag)
        return cls._spalte_aus_job(job, {**eintrag, 'rolle': 'variante'}, worker_lebt)

    @classmethod
    def _spalte_aus_job(cls, job, kopf, worker_lebt):
        spalte = {'id': kopf.get('id'), 'titel': kopf.get('titel'), 'rolle': kopf.get('rolle'), 'feld': kopf.get('feld'), 'wert': kopf.get('wert'),
                  'automatisch': bool(kopf.get('automatisch')),              # vom Import selbst angelegt (`Mesh3dvariantenauto`), nicht von Hand
                  'status': 'fehlt', 'prozent': 0, 'detail': '', 'fehler': '', 'werte': {}, 'bild': None, 'kennung': None, 'modell': ''}
        if job is None:
            return spalte
        from .meshfigurarbeiter import Meshfigurarbeiter

        status = job.status
        if status == 'laeuft' and kopf.get('rolle') == 'variante' and not worker_lebt and not Meshfigurarbeiter.lebt(job):
            status = 'gescheitert'                       # der Prozess ist weg, ohne den Auftrag abzuschließen
        spalte.update(status=status, prozent=job.progress or 0, detail=job.progress_detail or '', fehler=job.error_message or '', kennung=job.kennung, modell=job.modell or '',
                      werte=cls.werte(job.ergebnis or {}), bild=cls._bild(job))
        return spalte

    @staticmethod
    def _bild(job):
        from ..daten.meshfigurablage import Meshfigurablage

        pfad = Meshfigurablage(job.kennung).ergebnis('vergleich.jpg')
        if not pfad.is_file():
            return None
        return '%s?v=%d' % (reverse('meshfigur_datei', args=[job.id, 'ergebnis', 'vergleich.jpg']), int(pfad.stat().st_mtime))

    @staticmethod
    def werte(ergebnis):
        """Die Kennzahlen eines Laufs, flach, nach `ZEILEN` — aus `ergebnis.abnahme`; fehlt sie (Lauf vor dem 13.10.2026), nur Höhe und Abstand der Vorschau."""
        a = ergebnis.get('abnahme') if isinstance(ergebnis.get('abnahme'), dict) else {}
        vorschau = ergebnis.get('vorschau') or {}
        abstand = vorschau.get('abstand') or {}
        netz = a.get('figur_netz') or {}
        stoff = a.get('stoff_im_koerper') or {}
        teile = a.get('abstand_je_teil_mm') or {}
        masse = a.get('masse_cm') or {}
        objekte = a.get('objekte') or {}
        aus = {
            'figur_netz_rms_mm': netz.get('figur_netz_rms_mm', abstand.get('figur_netz_rms_mm')),
            'netz_figur_rms_mm': netz.get('netz_figur_rms_mm', abstand.get('netz_figur_rms_mm')),
            'stoff_im_koerper_prozent': stoff.get('unter_0_prozent'), 'stoff_tief_prozent': stoff.get('unter_5mm_prozent'),
            'hand_l_mm': teile.get('Hand L'), 'hand_r_mm': teile.get('Hand R'),
            'oberschenkel_cm': masse.get('oberschenkel_umfang'), 'huefte_cm': masse.get('huefte_umfang'), 'taille_cm': masse.get('taille_umfang'), 'brust_cm': masse.get('brust_umfang'),
            'hoehe_cm': a.get('hoehe_cm', vorschau.get('hoehe_cm')),
            'doppelt': objekte.get('doppelt'), 'waisen_rest': objekte.get('waisen_rest'),
        }
        return {k: (round(float(v), 2) if isinstance(v, (int, float)) else None) for k, v in aus.items()}

    # ----------------------------------------------------------- Empfehlung

    @classmethod
    def _gruppe(cls, f, stand, haupt, spalten, vorher):
        # Der erste Lauf trägt den Wert, mit dem er gerechnet wurde: nach „Übernehmen“ steht im Import schon der neue (`vorher` in `varianten.json`).
        wert = vorher.get(f['schluessel']) or Mesh3dvarianten.aktuell(stand, f['schluessel'])
        erste = {**haupt, 'feld': f['schluessel'], 'wert': wert}
        alle = [erste] + [s for s in spalten if s['status'] == 'fertig']
        return {'feld': f['schluessel'], 'titel': f['titel'], 'spalten': [erste] + spalten, 'empfehlung': cls.dominanz(alle) if haupt['status'] == 'fertig' else None}

    @classmethod
    def dominanz(cls, spalten):
        """`{id, wert, grund}` der Spalte, die jede andere im Gütemaß schlägt, sonst `None`. Weniger als zwei Spalten: `None`."""
        if len(spalten) < 2:
            return None
        sieger = [s for s in spalten if all(cls._schlaegt(s, a) for a in spalten if a is not s)]
        if len(sieger) != 1:
            return None
        s = sieger[0]
        besser = sorted({z for a in spalten if a is not s for z in cls._deutlich_besser(s, a)})
        titel = {k: t for k, t, _ in cls.ZEILEN}
        return {'id': s['id'], 'wert': s['wert'], 'grund': 'in keiner Zeile des Gütemaßes schlechter, deutlich besser bei: %s' % ', '.join(titel[z] for z in besser)}

    @classmethod
    def _vergleiche(cls, a, b):
        """`[(zeile, a−b, toleranz)]` für die Zeilen des Gütemaßes, in denen beide einen Wert haben."""
        return [(z, a['werte'][z] - b['werte'][z], tol) for z, tol in cls.GUETE.items() if a['werte'].get(z) is not None and b['werte'].get(z) is not None]

    @classmethod
    def _schlaegt(cls, a, b):
        v = cls._vergleiche(a, b)
        if len(v) < cls.MIN_ZEILEN:
            return False
        return all(d <= tol for _, d, tol in v) and any(d < -tol for _, d, tol in v)

    @classmethod
    def _deutlich_besser(cls, a, b):
        return [z for z, d, tol in cls._vergleiche(a, b) if d < -tol]

    @classmethod
    def empfehlungen(cls, stand, gruppen):
        """Je Feld, das die Seite zeigt: `{schluessel, titel, aktuell, empfohlen, quelle, text}`. `quelle`: `vergleich` (Dominanz der gerechneten Spalten), `regel` (gilt für jeden Auftrag dieses Wegs) oder `keine`."""
        aus = []
        je_feld = {g['feld']: g for g in gruppen}
        for f in Mesh3dvarianten.FELDER:
            aktuell = Mesh3dvarianten.aktuell(stand, f['schluessel'])
            gruppe = je_feld.get(f['schluessel']) or {}
            e = gruppe.get('empfehlung')
            if e:
                aus.append({'schluessel': f['schluessel'], 'titel': f['titel'], 'aktuell': aktuell, 'empfohlen': e['wert'], 'quelle': 'vergleich', 'text': e['grund'], 'id': e['id']})
                continue
            regel = cls.REGELN.get(f['schluessel'])
            aus.append({'schluessel': f['schluessel'], 'titel': f['titel'], 'aktuell': aktuell, 'empfohlen': regel['wert'] if regel else None,
                        'quelle': 'regel' if regel and regel['wert'] else 'keine', 'text': regel['text'] if regel else '', 'id': None})
        return aus

    #: Empfehlungen, die nicht an einem Lauf hängen (Konzept „ohne Nacharbeit“, Abschnitt 4): `wert` None = nur ein Hinweis.
    REGELN = {
        'pose': {'wert': 'sam', 'text': 'SAM 3D Body findet die Gelenke am Rendering des Netzes; alle Läufe dieses Wegs bisher liefen so (rund 12 s warm, 75 s kalt). MediaPipe auf Renderings ist die Vorgabe der anderen Wege.'},
        'kleidung_zug': {'wert': None, 'text': 'Vorgabe „ignorieren“: an anliegender Kleidung (Edgar) gleich gut wie „nah“, an lockerer (Robe, Reifenrock) bläht „nah“ Taille und Oberschenkel um 16–17 cm auf — dafür steht der Stoff mit „ignorieren“ öfter im Körper (Reifenrock 9,7 gegen 3,5 %). Unsicher: die Vergleichsvariante ansehen.'},
        'basis': {'wert': None, 'text': 'Die Grundfigur nach dem Geschlecht der Figur wählen — eine falsche bleibt ohne Fehlermeldung. Unsicher: Varianten rechnen.'},
    }
