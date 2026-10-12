# -*- coding: utf-8 -*-
u"""G9materialwahl — was in der Anfrage die MATERIALIEN bestimmt: Haut, Augen, Brauen, Presets, Brauenstil.

Aus `g9figur.py` herausgeloest (12.10.2026): Dieselbe Wahl braucht die volle Netzantwort (`G9figur._koerper`)
und die leichte nur mit Materialien (`G9materialnetzapi`) — an einer Stelle, damit beide dieselbe Haut meinen.
Ohne Angabe im Rumpf gelten Haut, Augen und Brauen des Eintrags — bei einem gespeicherten Modell die
gespeicherten.
"""

__all__ = ['G9materialwahl']


class G9materialwahl:
    u"""Presetnamen aus dem Rumpf lesen und bereinigen."""

    @staticmethod
    def name(wert):
        u"""Ein Presetname aus dem Rumpf — ohne Pfadzeichen, sonst None."""
        text = str(wert or '').strip()
        if not text or '/' in text or '\\' in text or '..' in text:
            return None
        return text[:80]

    @staticmethod
    def aus(rumpf, eintrag):
        u"""Die Wahl als Schluesselwoerter von `G9koerpernetz` (hautpreset, augen, brauen, praesets, brauenstil)."""
        name = G9materialwahl.name
        gespeichert = eintrag.get('gespeichert')
        return {
            'hautpreset': name(rumpf.get('haut')) or name(eintrag.get('haut') if gespeichert else None),
            'augen': name(rumpf.get('augen')) or name(eintrag.get('augen')) or '01',
            'brauen': name(rumpf.get('brauen')) or name(eintrag.get('brauen')),
            'praesets': (rumpf['praesets'] if isinstance(rumpf.get('praesets'), dict)
                         else eintrag.get('praesets') or {}),
            'brauenstil': name(rumpf.get('brauenstil')) or name(eintrag.get('brauenstil')),
        }
