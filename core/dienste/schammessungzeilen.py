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
        f = g.get('flaeche')
        if f:
            z.append('Fläche: Kantenwinkel Stück (Grad) %s | Original %s | Kanten über 90°: Stück %.1f %%, Original %.1f %%' % (
                cls._st(f['kantenwinkel_grad']), cls._st(f['kantenwinkel_original_grad']), f['ueber_90'] * 100, f['ueber_90_original'] * 100))
        s = g.get('symmetrie') or {}
        z.append('Symmetrie (Spiegelabstand zur Fläche, mm): Stück %s | Original %s' % (cls._st(s.get('stueck')), cls._st(s.get('original'))))
        z += cls._ansichten(m.get('ansichten') or {})
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
    def _ansichten(cls, a):
        """Erhebungen aus mehreren Richtungen und der Absatz am Ring (`Schammessungansichten`)."""
        z = []
        for r in a.get('ansichten', []):
            if r.get('hinweis'):
                z.append('Ansicht %s: %s' % (r['name'], r['hinweis']))
                continue
            z.append('Ansicht %-9s %5d Zellen: Erhebung Original %6d mm³ (Höhe p95 %s, größte %s mm) | Modell %6d mm³ (p95 %s, größte %s) | Treue %s | Senke Original %d / Modell %d mm³ | Abweichung Median %.2f p90 %.2f max %.1f mm' % (
                r['name'], r['zellen'], r['volumen_original_mm3'], *(r.get('hoehe_original_mm') or ['—', '—']), r['volumen_modell_mm3'], *(r.get('hoehe_modell_mm') or ['—', '—']),
                '%.2f' % r['treue'] if r.get('treue') is not None else '—', r['senke_original_mm3'], r['senke_modell_mm3'], r['abweichung']['median'], r['abweichung']['p90'], r['abweichung']['max']))
        s = a.get('absatz')
        if s:
            z.append('Absatz am Ring (Höhe %.0f mm hinter dem Ring über der Hautebene, %d Ringpunkte): Stück %s | Original %s; über 3 mm: Stück %d, Original %d; über 10 mm: Stück %d, Original %d' % (
                s['nach_innen_mm'], s['ringpunkte'], cls._st(s['stueck_mm']), cls._st(s['original_mm']), s['stueck_ueber_3mm'], s['original_ueber_3mm'], s['stueck_ueber_10mm'], s['original_ueber_10mm']))
        return z

    @classmethod
    def _naht(cls, n):
        if not n:               # das Stück hat keine Naht-Angaben (`zeilen` reicht `{}` durch) — vorher KeyError 'randpunkte' bei „Farbe am Ring" im Lauf Fallout ranger, 12.10.2026
            return ['Naht: keine Angaben']
        if n.get('hinweis'):
            return ['Naht: ' + n['hinweis']]
        if n.get('aus'):        # das Stück trägt keine Naht (`Blendimportschamgeograft`: `{'aus': Grund}`) — vorher KeyError 'randpunkte' im Lauf Fallout ranger, 12.10.2026
            return ['Naht: aus — %s' % str(n['aus'])[:200]]
        z = ['Naht: %d Randpunkte, %d Ringecken; Rand → Ring %s | Ring → Rand %s' % (n['randpunkte'], n['ringecken'], cls._st(n['rand_zu_ring_mm']), cls._st(n['ring_zu_rand_mm']))]
        if n.get('ring_glaettung_mm'):
            z.append('  Glättung des Rings gegen die Haut (mm): %s' % cls._st(n['ring_glaettung_mm']))
        w = n['normalen_grad']
        z.append('  Normalenwinkel Stück ↔ Haut am Rand (Grad): Median %.1f, p90 %.1f, max %.1f; umgekehrt %.0f %%' % (w['median'], w['p90'], w['max'], w['umgekehrt'] * 100))
        q = n.get('knick_ueber_naht')
        if q and q.get('kanten'):
            z.append('  Knick über die Naht je Ringkante (Haut ↔ Stück, Grad): %d Kanten, Median %.1f, p90 %.1f, max %.1f; über 30°: %d, über 60°: %d, über 90°: %d; schlimmste (Ringecke, Grad) %s' % (
                q['kanten'], q['median_grad'], q['p90_grad'], q['max_grad'], q['ueber_30'], q['ueber_60'], q['ueber_90'], q['schlimmste']))
        k = n.get('kanten_am_rand')
        if k:
            z.append('  Knicke der Fläche im Band 12 mm am Rand: %d Kanten, Median %.1f°, über 60° %.1f %%, über 90° %.1f %%' % (k['kanten'], k['median_grad'], k['ueber_60'] * 100, k['ueber_90'] * 100))
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
