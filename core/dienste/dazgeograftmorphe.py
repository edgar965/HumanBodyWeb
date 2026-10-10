# -*- coding: utf-8 -*-
"""Dazgeograftmorphe — die Formmorphe des Daz-Geografts als Regler des Stücks (10.10.2026).

Edgar: „baue die Morphs in das UI ein". Was Daz mitliefert (`Dazgeograftquelle`, gemessen 10.10.2026):

    body_bs_Uncircumcised_HD3   1.509 Deltas  Vorgabe 0   → Regler `daz_vorhaut`        „Vorhaut" 0 … 1 (männliches Geograft)
    body_bs_GenitalRealism_HD3  1.511 Deltas  Vorgabe 1   → Regler `daz_realism_aus`    „Realism HD aus" 0 … 1 (beide); das Stück wird MIT Realism gebaut
    Penile Length / Width       Knochenformeln (`Gen2…Gen6` Verschiebung und Skalierung)  → kein Formmorph: dieselben Griffe sind `pen_laenge` und `pen_umfang`
    Testes Asymmetry            Knochenformel (`rTeste`/`lTeste`)                         → `pen_hoden_asymmetrie` (Katalog des Penis, gilt für jedes Stück mit Penis)

Ein Formmorph des Geografts ist ein Satz Deltas auf seinen Käfigpunkten (männlich 1.516); das Stück liegt auf Stufe 1. Die Deltas gehen deshalb durch dieselbe
Catmull-Clark-Matrix (Unterschied der Stufe-1-Punkte mit und ohne Morph) und werden auf die Punkte des Stücks übertragen (nächster Punkt, höchstens `MAX_ABSTAND_M`).
Abgelegt wird wie jeder eigene Morph (`G9kleidmorphe.ablegen`), mit dem Feld `regler` im Steckbrief (Name, Grenzen, Gruppe: `G9kleidmorphebrief`).
"""
import logging

logger = logging.getLogger('core')

__all__ = ['Dazgeograftmorphe']


class Dazgeograftmorphe:
    #: Nächster Stufe-1-Punkt höchstens so weit (m) vom Punkt des Stücks (der Rand wanderte bei der Naht bis 3,4 mm).
    MAX_ABSTAND_M = 0.01
    #: `(Reglername, Daz-Morph, Vorzeichen des Deltas, Geschlecht oder None = beide, Regler)`.
    MORPHE = (
        ('daz_vorhaut', 'body_bs_Uncircumcised_HD3', 1.0, 'mann',
         {'anzeige': 'Vorhaut (beschnitten ↔ unbeschnitten)', 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'gruppe': 'Penis · Daz'}),
        ('daz_realism_aus', 'body_bs_GenitalRealism_HD3', -1.0, None,
         {'anzeige': 'Realism HD aus (Daz)', 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'gruppe': 'Anatomie · Daz'}),
    )

    @classmethod
    def ablegen(cls, bau, quelle, kaefig, stueck):
        """Die Formmorphe von `quelle` als Regler des Stücks `stueck` (Garderobenkennung) ablegen → Namen. `bau`: der `Dazgeograft` (für `stufe_punkte`)."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.kleidmorphe import G9kleidmorphe
        from scipy.spatial import cKDTree

        G9garderobe.vergessen()
        teile, kaefige, _y0, _y1, _mitte, _eintrag = G9kleidmorphe.kaefige(stueck)
        if len(teile) != 1:
            raise ValueError('%s hat %d Teile — erwartet EINS' % (stueck, len(teile)))
        ziel = kaefige[0]
        stufe0 = bau.stufe_punkte(quelle, kaefig)
        abstand, nummer = cKDTree(stufe0).query(ziel)
        if float(abstand.max()) > cls.MAX_ABSTAND_M:
            raise ValueError('Ein Punkt des Stücks liegt %.1f mm vom Geograft entfernt (Grenze %.0f mm)' % (abstand.max() * 1000.0, cls.MAX_ABSTAND_M * 1000.0))
        namen = []
        for name, morph, vorzeichen, geschlecht, regler in cls.MORPHE:
            if geschlecht not in (None, quelle.geschlecht):
                continue
            delta = bau.stufe_punkte(quelle, kaefig + vorzeichen * quelle.morph(morph)) - stufe0
            G9kleidmorphe.ablegen(stueck, name, [f.kennung for f, _lage in teile], [delta[nummer]],
                                  {'regler': regler, 'daz_morph': morph, 'vorzeichen': vorzeichen})
            namen.append(name)
        return namen

    @classmethod
    def katalog_bauen(cls, stueck, anatomie):
        """Alle Regler des Anatomie-Katalogs (`pen_*` | `sch_*`) einmal bauen, damit der erste Zug im UI nicht warten muss → `(gebaut, gescheitert)`."""
        from Genesis9.standardmorphe import G9standardmorphe

        gebaut, gescheitert = [], {}
        for eintrag in anatomie.eintraege():
            try:
                G9standardmorphe.bauen(stueck, eintrag[0])
                gebaut.append(eintrag[0])
            except (ValueError, OSError, KeyError, IndexError) as fehler:
                gescheitert[eintrag[0]] = str(fehler)[:160]
                logger.warning('Daz-Geograft %s: Regler %s nicht gebaut: %s', stueck, eintrag[0], fehler)
        return gebaut, gescheitert
