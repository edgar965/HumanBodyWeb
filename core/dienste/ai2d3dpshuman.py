# -*- coding: utf-8 -*-
"""Ai2d3dpshuman — ob und wie PSHuman (Li et al., CVPR 2025, Code pengHTYX/PSHuman) die Genesis-Figur eines
2d-3d-AI-Jobs mitbestimmt (03.11.2026).

Edgar: „lege danach die Jobs mit dem pshuman an. pshuman als Option bei den jobs. und passe die Genesis
Generierung an mit pshuman“ — dann „mach beides, selektierbar“. PSHuman macht aus dem Vorderfoto 6 Ansichten
und daraus ein farbiges Netz (`pshuman_port14/pshuman_job_rechnen.py`,
Ablage `<Job>/pshuman/`).

In `3DObjects/ai2d3d/<Name>/job.json` als `pshuman`: {zeile1, drehteller} (zwei Häkchen, frei kombinierbar);
fehlt es, ist beides aus — PSHuman fließt dann nicht in die Figur (das Netz steht höchstens im Feld „Netz“).
Der Silhouettenkonsens läuft nur mit einer Zeile 1 (`Fotoauswendig.figur`: sonst „keine Stücke der Zeile 1“) —
in einem Job ohne eigene Zeile 1 wirkt der Drehteller also erst zusammen mit `zeile1`.
  drehteller   das PSHuman-Netz, an die Figur des Vorderfotos angelegt, aus vielen Richtungen gerendert: seine
               Umrisse gehen als weitere Bilder in den Silhouettenkonsens von videoavatars
               (`KoerperKI_Fotos.fotodrehteller.Fotodrehteller`, Körperstufe), wie dort ein Mensch,
               der sich dreht
  zeile1       das PSHuman-Netz ist das Netz der Zeile 1: Mesh → Genesis (IPNet-Port `G9meshgenesis`), danach
               Zeile 2 wie bisher mit den Reglern und Stücken der Zeile 1
Seit 03.11.2026 abends (Edgar: „mach im job ein UI das entweder eines oder mehrere Bilder nimmt“), seit 04.11.2026 als Zahl
(„Auswahl anzahl der fotos (1-6), wenn mehrere fotos dann Hochladen funktion bei den Ansichten“):
  anzahl         1 (Vorgabe): PSHuman bekommt nur „vorn“ und erfindet die übrigen Ansichten;
                 2–6: so viele echte Fotos statt erfundener Ansichten (Bildplätze `Ai2d3dpshumaneingabe`,
                 job.json `pshuman.eingabe` — bleibt beim Speichern hier unangetastet); Rechenweg
                 `pshuman_port14/mehrbild.py`, noch nie gelaufen
  vae_bildweise  eigene Zutat: der VAE-Dekoder rechnet die 14 Bilder einzeln (diffusers
                 `enable_vae_slicing`) — gemessen 03.11.2026 (`ProjektTemp/_wegwerf/textur/original/pshuman_port14_proben/vae_zeit.py`): bitgleich,
                 2,1 statt 120 s, +1,9 statt +27,6 GB
  genesis_aus_foto  Edgar 04.11.2026: „mach eine auswahl ob das Genesis modell direkt aus dem foto gerechnet werden soll, default aus“, „mach das auch ganz oben“ — die
                 Foto-Kette (`nurfotos_kette.py`, Feld „Genesis – 2d3dai (aus Fotos)“) rechnet nur mit diesem Häkchen; sonst endet sie gleich
  dichte         Edgar 04.11.2026: „die Auflösung im pshuman mesh ist ja nicht so gut wie im Foto“, „mach beides, einstellbar ganz oben beim Job“: Punkte je Körperhöhe des Netzes
                 (`pshuman_port14/poissontorch.py`): 480 = so viele wie bisher, 960 = viermal so viele Punkte; die Glättung hängt seit 05.11.2026 an der Körperhöhe, die Form bleibt
  fototextur     Textur aus den Fotos in voller Auflösung statt Punktfarben (`pshuman_port14/fototextur.py`); erfundene Ansichten bleiben bei 768 Pixeln
  up2you         Edgar 05.11.2026: „machst du den edgar alle job mit Up2you?“: UP2You rechnet aus allen Fotos des Jobs sechs Ansichten in A-Pose und daraus das Netz, statt PSHumans Diffusion (`pshuman_port14/up2youlauf.py`)
  hand_ersatz    Edgar 05.11.2026 zu Edgar 1: „die Hände sind kaputt“: PSHumans `replace_hand` setzt die Hand der eingepassten Genesis-Figur ins Netz, wo MediaPipe sie meldet (`pshuman_port14/handersatz.py`, `genesishand.py`, `MediapipeTorch/handpunkte.py`), seit 07.11.2026 statt der Hand des SMPL-X; UP2You nimmt die Hand seines SMPL-X (`up2youlauf.py`)
  haut_ki        Edgar 05.11.2026: „Sollten wir im UI oben beim Job eine Checkbox machen - Haut KI?“, seit 06.11.2026 Vorgabe aus (`Hautohneki`, Messung dort): Aus schreibt der Schritt „Haut“ von Mesh3D-AI die Kacheln ohne Netz (`mesh3dai/mesh3dai_haut_ohneki.py`, liest diese Wahl selbst); PSHuman rechnet deshalb nicht neu
  keine_kleider  Edgar 06.11.2026 zu n2: „mach n2 mit: keine Kleider“: In der Kostüm-Erkennung wird alles außer Haar zu Haut (`mesh3dai/mesh3dai_kostuem_ohnekleider.py`, liest diese Wahl selbst); PSHuman rechnet deshalb nicht neu

    POST /api/2d3dai/<job>/pshuman/   {zeile1, drehteller, vae_bildweise, genesis_aus_foto, fototextur, hand_ersatz, up2you, haut_ki, keine_kleider, anzahl, dichte}   → {ok, pshuman}
"""

import json
import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dpshuman']


class Ai2d3dpshuman:
    FELD = 'pshuman'
    VORGABE = {'zeile1': False, 'drehteller': False, 'vae_bildweise': False, 'genesis_aus_foto': False, 'fototextur': False, 'hand_ersatz': False, 'up2you': False, 'haut_ki': False, 'keine_kleider': False}  # noqa: RUF012 — nur gelesen
    WEGE = (('zeile1', 'Netz als Zeile 1'), ('drehteller', 'Drehteller'), ('vae_bildweise', 'VAE bildweise'),
            ('genesis_aus_foto', 'Genesis direkt aus dem Foto'), ('fototextur', 'Textur aus den Fotos'), ('hand_ersatz', 'Hände ersetzen'), ('up2you', 'Ansichten aus UP2You'), ('haut_ki', 'Haut-KI'), ('keine_kleider', 'Keine Kleider'))
    ANZAHL = (1, 2, 3, 4, 5, 6)
    DICHTEN = ((480, 'normal'), (960, 'dicht'))
    BESCHREIBUNG = {  # noqa: RUF012 — nur gelesen
        'keine_kleider': 'Die Person im Foto trägt nichts: Die Kostüm-Erkennung wertet alles außer Haar als Haut, die Figur bekommt keine Kleider und keine Stücke, nur das Haar. '
                         'Aus (Vorgabe): Die Bilderkennung entscheidet. Wirkt in Mesh3D-AI ab dem nächsten Lauf.',
        'haut_ki': 'Aus (Vorgabe): Die gesehene Haut kommt unverändert aus dem Netz, mit dem Licht des Fotos. '
                   'An: Die Haut-KI rechnet die Hautkacheln der Genesis-Figur, nimmt das Licht des Fotos heraus und glättet Stellen mit Kleiderfarbe oder Flecken, verliert dabei aber Zeichnung. '
                   'Ungesehene Haut wird in beiden Fällen ergänzt. Wirkt im Schritt „Haut“ von Mesh3D-AI.',
        'up2you': 'UP2You rechnet aus allen Fotos des Jobs sechs Ansichten in A-Pose und daraus das Netz, statt PSHumans Diffusion. Die Fotos zeigen eine andere Haltung, darum gilt „Textur aus den Fotos“ hier nicht: Die Farbe kommt aus den Ansichten (768 Pixel).',
        'hand_ersatz': 'Im PSHuman-Netz sind die Finger oft verschmolzen. An: Wo MediaPipe eine Hand meldet, kommt die Hand der Genesis-Figur ins Netz, Finger und Handgelenk wie im Foto. Mit UP2You: die Hand aus dessen SMPL-X.',
        'fototextur': 'Das PSHuman-Netz bekommt eine Textur aus den Fotos in voller Auflösung statt Farben je Punkt. Ansichten ohne Foto bleiben so scharf wie PSHuman sie erfindet (768 Pixel).',
        'genesis_aus_foto': 'Die Foto-Kette rechnet das Genesis-Modell direkt aus den Fotos (Feld „Genesis – 2d3dai (aus Fotos)“). '
                            'Aus: sie rechnet für diesen Job nicht; das Genesis-Modell kommt nur aus dem PSHuman-Netz (Mesh3D-AI).',
        'vae_bildweise': 'Eigene Zutat (diffusers enable_vae_slicing): der VAE-Dekoder der Diffusion rechnet '
                         'die 14 Bilder einzeln statt auf einmal — gemessen bitgleich, 2,1 s statt 120 s, '
                         '+1,9 GB statt +27,6 GB Grafikspeicher.',
        'zeile1': 'Das PSHuman-Netz ist das Netz der Zeile 1: die vorhandene Einpassung Mesh → Genesis '
                  '(IPNet-Port) legt die Genesis-Figur hinein, Zeile 2 übernimmt deren Regler und Stücke.',
        'drehteller': 'Das PSHuman-Netz wird an die Figur des Vorderfotos angelegt und aus vielen Richtungen '
                      'gerendert; seine Umrisse gehen als weitere Bilder in den Silhouettenkonsens von '
                      'videoavatars (dort: ein Mensch, der sich dreht, 120 Bilder). Braucht eine Zeile 1.',
    }

    @classmethod
    def auswahl(cls):
        """Häkchen „PSHuman“: {Name: {Text, Beschreibung}}; die Vorlage liest nach Namen, nicht nach Stelle."""
        return {w: {'wert': w, 'text': t, 'beschreibung': cls.BESCHREIBUNG[w]} for w, t in cls.WEGE}

    @classmethod
    def lesen(cls, info):
        """Die Wahl aus einer job.json samt Vorgabe (fehlende Häkchen aus)."""
        roh = info.get(cls.FELD) or {}
        anzahl, dichte = roh.get('anzahl'), roh.get('dichte')
        return dict({k: bool(roh.get(k, v)) for k, v in cls.VORGABE.items()},
                    anzahl=int(anzahl) if anzahl in cls.ANZAHL else cls.ANZAHL[0],
                    dichte=int(dichte) if dichte in dict(cls.DICHTEN) else cls.DICHTEN[0][0])

    @classmethod
    def gerechnet(cls, ordner):
        """Zeitpunkt, zu dem PSHuman für den Job fertig wurde (`pshuman/befund.json` `fertig`), oder None."""
        try:
            return json.loads((ordner / 'pshuman' / 'befund.json').read_text(encoding='utf-8')).get('fertig')
        except (OSError, ValueError):
            return None

    @classmethod
    def setzen(cls, job, rumpf):
        """Schreibt die Wahl in die job.json (mischend). `ValueError` bei unbekanntem Feld."""
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine PSHuman-Wahl')
        fremd = sorted(set(rumpf) - set(cls.VORGABE) - {'anzahl', 'dichte'})
        if fremd:
            raise ValueError('Unbekannte Felder %s' % (fremd,))
        if 'anzahl' in rumpf and (isinstance(rumpf['anzahl'], bool) or rumpf['anzahl'] not in cls.ANZAHL):
            raise ValueError('anzahl %r: erlaubt %d bis %d' % (rumpf['anzahl'], cls.ANZAHL[0], cls.ANZAHL[-1]))
        if 'dichte' in rumpf and (isinstance(rumpf['dichte'], bool) or rumpf['dichte'] not in dict(cls.DICHTEN)):
            raise ValueError('dichte %r: erlaubt %s' % (rumpf['dichte'], ', '.join(str(d) for d, _t in cls.DICHTEN)))
        datei = job['ordner'] / 'job.json'
        info = json.loads(datei.read_text(encoding='utf-8'))
        # 'weg' der ersten Fassung (03.11.2026, Combo-Box) fällt weg; die Bildplätze ('eingabe',
        # `Ai2d3dpshumaneingabe`) bleiben
        behalten = set(cls.VORGABE) | {'anzahl', 'dichte', 'eingabe'}
        neu_wahl = {k: bool(rumpf[k]) for k in cls.VORGABE if k in rumpf}
        if 'anzahl' in rumpf:
            neu_wahl['anzahl'] = int(rumpf['anzahl'])
        if 'dichte' in rumpf:
            neu_wahl['dichte'] = int(rumpf['dichte'])
        alt = {k: v for k, v in (info.get(cls.FELD) or {}).items() if k in behalten}
        info[cls.FELD] = dict(alt, **neu_wahl)
        neu = datei.with_name('job.json.neu')
        neu.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        logger.info('Ai2d3dpshuman: %s → %s', datei, info[cls.FELD])
        return cls.lesen(info)
