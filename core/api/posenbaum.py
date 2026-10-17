# -*- coding: utf-8 -*-
"""Der Ordnerbaum aller Posen (HumanBody + Genesis 9) und seine Verwaltung (17.10.2026).

    GET  /api/character/posenbaum/            -> `Posenbaum.baum`
    POST /api/character/posenbaum/verwalten/  {bestand, action, …}

Aktionen (je Bestand dieselben, damit das Kontextmenue eines ist):

    move           {id, target}         Pose in einen (auch neuen) Ordner
    delete         {id}                 Pose loeschen
    new_folder     {parent, name}       Ordner anlegen (`parent` leer = oberste Ebene)
    rename_folder  {folder, new_name}   letzten Teil des Ordners umbenennen
    delete_folder  {folder}             Ordner mit allen Posen darin loeschen

`humanbody` aendert die Platte unter `poseData/` (`Posenordner`, Geloeschtes in
`.trash/`); `genesis9` nur die Einteilung neben der Daz-Bibliothek
(`G9poseneinteilung`, Geloeschtes wird ausgeblendet). Umbenennen und Speichern
einer HumanBody-Pose bleiben bei `/api/character/pose-manage/` (`Posen`).
"""

import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.anfragerumpf import Anfragerumpf
from ..dienste.posenablage import PosenFehler
from ..dienste.posenbaum import Posenbaum
from ..dienste.posenordner import Posenordner
from .posen import Posen

logger = logging.getLogger('core')

__all__ = ['Posenbaumapi']


class Posenbaumapi:
    """Die beiden Endpunkte des Reiters „Posen"."""

    @staticmethod
    @require_GET
    def baum(request):
        return JsonResponse(Posenbaum.baum(Posen.wurzel()))

    @staticmethod
    @csrf_exempt
    @require_POST
    def verwalten(request):
        daten, fehler = Anfragerumpf.lesen(request)
        if fehler:
            return fehler
        bestand, aktion = daten.get('bestand', ''), daten.get('action', '')
        logger.info('[posenbaum] bestand=%s action=%s id=%s folder=%s target=%s new_name=%s',
                    bestand, aktion, daten.get('id'), daten.get('folder'), daten.get('target'),
                    daten.get('new_name'))
        try:
            if bestand == 'humanbody':
                ergebnis = Posenbaumapi._humanbody(aktion, daten)
            elif bestand == 'genesis9':
                ergebnis = Posenbaumapi._genesis9(aktion, daten)
            else:
                raise PosenFehler(f'Unbekannter Bestand: {bestand}')
        except PosenFehler as abgelehnt:
            logger.info('[posenbaum] abgelehnt (%d): %s', abgelehnt.kennzahl, abgelehnt.text)
            return JsonResponse({'error': abgelehnt.text}, status=abgelehnt.kennzahl)
        return JsonResponse(ergebnis)

    # ---------------------------------------------------------- HumanBody

    @staticmethod
    def _humanbody(aktion, daten):
        wurzel = Posen.wurzel()
        if aktion == 'move':
            return Posenordner.verschieben(wurzel, daten.get('id'), daten.get('target'))
        if aktion == 'delete':
            return Posenordner.loeschen(wurzel, daten.get('id'))
        if aktion == 'new_folder':
            return Posenordner.ordner_anlegen(wurzel, daten.get('parent') or '', daten.get('name'))
        if aktion == 'rename_folder':
            return Posenordner.ordner_umbenennen(wurzel, daten.get('folder') or '', daten.get('new_name'))
        if aktion == 'delete_folder':
            return Posenordner.ordner_loeschen(wurzel, daten.get('folder') or '')
        raise PosenFehler(f'Unbekannte Aktion: {aktion}')

    # ---------------------------------------------------------- Genesis 9

    @staticmethod
    def _genesis9(aktion, daten):
        from Genesis9.posen import G9posen
        from Genesis9.poseneinteilung import G9poseneinteilung

        katalog = G9posen.katalog()
        try:
            if aktion in ('move', 'delete'):
                eintrag = katalog.get(str(daten.get('id') or ''))
                if eintrag is None:
                    raise PosenFehler(f'Pose „{daten.get("id")}" gibt es nicht.', 404)
                if aktion == 'delete':
                    G9poseneinteilung.ausblenden([eintrag['id']])
                    return {'ok': True, 'ausgeblendet': 1}
                return {'ok': True, 'id': eintrag['id'],
                        'ordner': G9poseneinteilung.verschieben(eintrag, daten.get('target'))}
            if aktion == 'new_folder':
                name = str(daten.get('name') or '').strip()
                if '/' in name:
                    raise PosenFehler('Ein Ordnername ohne „/".')
                eltern = str(daten.get('parent') or '').strip('/')
                pfad = G9poseneinteilung.ordner_anlegen(f'{eltern}/{name}' if eltern else name)
                return {'ok': True, 'pfad': pfad}
            if aktion == 'rename_folder':
                neu = str(daten.get('new_name') or '').strip()
                if '/' in neu:
                    raise PosenFehler('Ein Ordnername ohne „/".')
                pfad = G9poseneinteilung.ordner_umbenennen(daten.get('folder'), neu, katalog)
                return {'ok': True, 'pfad': pfad}
            if aktion == 'delete_folder':
                return {'ok': True, 'posen': G9poseneinteilung.ordner_loeschen(daten.get('folder'), katalog)}
        except ValueError as abgelehnt:
            text = str(abgelehnt)
            raise PosenFehler(text, 409 if 'gibt es schon' in text else 400) from abgelehnt
        raise PosenFehler(f'Unbekannte Aktion: {aktion}')
