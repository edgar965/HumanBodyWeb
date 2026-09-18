# -*- coding: utf-8 -*-
u"""Figurkoepfe — Kopfmodelle ohne Körper, getrennt von den Ganzkörpern.

Edgar (17.09.2026): „ich brauche ganze Körper, mach getrennte Liste für nur
Kopf". Dieselben Felder wie `Figurquellen.ZEILEN`, damit Tabelle und Karten
der Seite „Hilfe → Architektur → Andere Modelle" beide Listen mit derselben
Vorlage zeigen; Rang und Vergleichszahl (Dreiecke) rechnet `Netzmasse`.
Zahlen von den Herstellerseiten (17.09.2026); wo eine Seite keine Netzzahl
nennt, steht das da, und die Zeile bekommt keinen Rang.
"""
from .netzmasse import Netzmasse

__all__ = ['Figurkoepfe']


class Figurkoepfe:
    u"""Rangliste der Kopfmodelle, absteigend nach Dreiecken der höchsten Stufe."""

    ZEILEN = [
        {'ordner': '19_TexturingXYZ_VFace_Kopf',
         'name': 'Texturing.xyz VFace', 'zusatz': 'Sammlung echter Köpfe',
         'punkte': None, 'vierecke': None, 'dreiecke': None,
         'stufen': 7, 'hoechste': 69_000_000, 'hoechste_einheit': 'punkte',
         'stufen_text': '7 Unterteilungen (Basis nicht angegeben)',
         'texturen': '16K Albedo + Displacement (32 bit), Normal, Cavity',
         'geschlecht': 'beide (Sammlung)', 'rig': '–',
         'preis': '39,90 $ je Kopf', 'lizenz': 'privat; kommerziell 299,90 $',
         'urteil': 'Das dichteste Netz der ganzen Suche — Haut in '
                   'Porenqualität, aber nur der Kopf.'},
        {'ordner': '09_Eisko_Louise_FreakyHoody',
         'bildmuster': 'Louise', 'linkschluessel': 'eisko_louise',
         'name': 'Eisko Louise', 'zusatz': 'eine Frau',
         'punkte': None, 'vierecke': None, 'dreiecke': 20_000_000,
         'stufen': None, 'stufen_text': 'roher Scan („20 Mio. Polygone")',
         'texturen': '4K PBR (Diffuse, Spec, Normal, Displacement, Gloss, '
                     'Rauheit)',
         'geschlecht': 'nur Frau', 'rig': 'FACS, 236 Blendshapes',
         'preis': 'kostenlos', 'lizenz': 'CC-BY-NC-ND — keine Ableitungen',
         'urteil': 'Referenz für Mimik (236 Blendshapes); die Lizenz '
                   'verbietet Ableitungen.'},
        {'ordner': '03_3DScanStore_frei', 'linkschluessel': '3dss_kopf_frei',
         'name': '3D Scan Store „Multi Expression Base Mesh"',
         'zusatz': 'kostenloser Kopf mit Ausdrücken',
         'punkte': None, 'vierecke': None, 'dreiecke': None,
         'stufen': 3, 'stufen_text': 'Stufen 1–3 (Basis nicht angegeben)',
         'texturen': 'passend zu 16K Albedo + HD-Displacement (nicht enthalten)',
         'geschlecht': 'nicht angegeben', 'rig': 'Ausdrücke als Netze',
         'preis': 'kostenlos (Newsletter)',
         'lizenz': 'privat (Personal Single User)',
         'urteil': 'Dasselbe Haus wie die Ganzkörper-Basen; ohne Netzzahl '
                   'kein Rang.'},
        {'ordner': '04_Ten24_SampleScan', 'bildmuster': 'Head',
         'linkschluessel': 'ten24_kopf',
         'name': 'Ten24 / 3D Scan Store freier Kopfscan',
         'zusatz': 'eine Frau, 2023',
         'punkte': None, 'vierecke': None, 'dreiecke': None,
         'stufen': None, 'stufen_text': 'ZTL, OBJ, FBX (Zahl nicht angegeben)',
         'texturen': '8K Albedo, Normal, Displacement (16-bit TIFF), Rauheit, '
                     'Spec',
         'geschlecht': 'nur Frau', 'rig': '–',
         'preis': 'kostenlos (Newsletter)', 'lizenz': 'privat/nicht-kommerziell',
         'urteil': 'Freie 8K-Kopfhaut zum Backen; ohne Netzzahl kein Rang.'},
    ]

    @classmethod
    def rangliste(cls):
        return Netzmasse.rangfolge(cls.ZEILEN)

    @classmethod
    def mit_rang(cls):
        return [e for e in cls.rangliste() if e['rang'] is not None]

    @classmethod
    def ohne_rang(cls):
        return [e for e in cls.rangliste() if e['rang'] is None]
