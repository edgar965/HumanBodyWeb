# -*- coding: utf-8 -*-
"""Datenklassen statt Dictionaries.

Regel aus dem Umbauauftrag: Ein Datensatz mit mehr als drei Feldern, der seine
Funktion verlaesst und anderswo per `["schluessel"]` gelesen wird, ist eine
Klasse. Ausgenommen bleibt, was sofort als JSON zum Browser geht oder so in der
Datenbank liegt — dort ist das Dictionary die Zielform.
"""
