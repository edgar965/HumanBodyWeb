# -*- coding: utf-8 -*-
"""Schammessungzeilen — der Bericht der `Schammessung` als lesbare Zeilen (10.10.2026)."""

__all__ = ['Schammessungzeilen']


class Schammessungzeilen:
    @classmethod
    def zeilen(cls, m):
        if m.get('fehler'):
            return ['MESSUNG GESCHEITERT: %s' % m['fehler']]
        z = ['Stück: %(punkte)d Punkte, %(dreiecke)d Dreiecke' % m['stueck']]
        g = m.get('geometrie') or {}
        z += cls._form(g)
        z += cls._tiefe(g.get('tiefenkarte'))
        s = g.get('symmetrie') or {}
        z.append('Symmetrie (Spiegelabstand zur Fläche, mm): Stück %s | Original %s' % (cls._st(s.get('stueck')), cls._st(s.get('original'))))
        z += cls._naht(m.get('naht') or {})
        z += cls._farbe(m)
        a = m.get('abweichungen') or []
        z.append('ABWEICHUNGEN (%d):' % len(a) if a else 'keine Abweichung über den Schwellen')
        return z + ['  - ' + t for t in a]

    @staticmethod
    def _st(s):
        return 'n %d, Median %.2f, p90 %.2f, max %.1f' % (s['n'], s['median'], s['p90'], s['max']) if s else '—'

    @classmethod
    def _form(cls, g):
        z = []
        o = g.get('original_zu_modell')
        if o:
            z.append('Form Original → Modell (mm): %s; innerhalb 1 mm %.0f %%, 2 mm %.0f %%' % (cls._st(o['gesamt']), o['innerhalb_1mm'] * 100, o['innerhalb_2mm'] * 100))
            z += ['  %-26s n %5d  Median %5.2f  p90 %5.2f  max %5.1f' % (r['zone'], r['n'], r['median'], r['p90'], r['max']) for r in o['zonen']]
        s = g.get('stueck_zu_original')
        if s:
            z.append('Stück → Original (mm): %s' % cls._st(s['gesamt']))
        if g.get('hinweis'):
            z.append(g['hinweis'])
        return z

    @classmethod
    def _tiefe(cls, t):
        if not t:
            return []
        if t.get('hinweis'):
            return ['Tiefenkarte: ' + t['hinweis']]
        z = ['Tiefenkarte (%d von %d Strahlen auf beiden): mittlerer Unterschied Modell − Original %+.2f mm; Betrag %s' % (t['beide_getroffen'], t['strahlen'], t['bias_mm'], cls._st(t['betrag']))]
        z += ['  %-26s n %5d  Median %5.2f  p90 %5.2f  max %5.1f' % (r['zone'], r['n'], r['median'], r['p90'], r['max']) for r in t['zonen']]
        z.append('  Mittelschnitt (quer 0): längs mm | Original | Modell | Unterschied (Tiefe relativ zur Ringmitte, + = vor)')
        z += ['    %6.1f | %6.2f | %6.2f | %+5.2f' % (r['laengs_mm'], r['original_mm'], r['modell_mm'], r['d_mm']) for r in t['profil_mitte']]
        return z

    @classmethod
    def _naht(cls, n):
        if n.get('hinweis'):
            return ['Naht: ' + n['hinweis']]
        z = ['Naht: %d Randpunkte, %d Ringecken; Rand → Ring %s | Ring → Rand %s' % (n['randpunkte'], n['ringecken'], cls._st(n['rand_zu_ring_mm']), cls._st(n['ring_zu_rand_mm']))]
        if n.get('ring_glaettung_mm'):
            z.append('  Glättung des Rings gegen die Haut (mm): %s' % cls._st(n['ring_glaettung_mm']))
        w = n['normalen_grad']
        z.append('  Normalenwinkel Stück ↔ Haut am Rand (Grad): Median %.1f, p90 %.1f, max %.1f; umgekehrt %.0f %%' % (w['median'], w['p90'], w['max'], w['umgekehrt'] * 100))
        return z

    @classmethod
    def _farbe(cls, m):
        z = []
        r = m.get('farbe_am_ring') or {}
        if r.get('hinweis'):
            z.append('Farbe am Ring: ' + r['hinweis'])
        elif r:
            z.append('Farbe am Ring: Stück am Rand RGB %s (%d Ecken)' % (r['stueck_rand']['rgb'], r['stueck_rand']['n']))
            for b in r['baender']:
                z.append('  Haut %s mm daneben: %s' % (b['band_mm'], 'RGB %s, Δ %.1f, Leuchtdichte Stück %+.1f %% (%d Dreiecke)' % (b['rgb'], b['delta_rgb'], b['leuchtdichte_prozent'], b['n'])
                                                        if b.get('n') else 'keine Dreiecke'))
        o = m.get('farbe_gegen_original') or {}
        if o.get('hinweis'):
            z.append('Farbe gegen Original: ' + o['hinweis'])
        elif o:
            z.append('Farbe gegen Original (Ecken ≤ %.0f mm vom Original, %d): mittlerer Kanalunterschied %.1f, Anteil über 12: %.0f %%' % (o['nah_mm'], o['ecken'], o['mittel'], o['anteil_anders'] * 100))
            z += ['  %-26s n %5d  Unterschied %5.1f  anders %3.0f %%' % (q['zone'], q['n'], q['mittel'], q['anteil_anders'] * 100) for q in o['zonen']]
        return z
