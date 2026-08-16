# -*- coding: utf-8 -*-
"""Django-Endpunkte, nach Themen getrennt.

Jedes Modul hier ist eine duenne Schicht: Anfrage lesen, eine Klasse aus
`core/dienste/` rufen, Antwort bauen. Was rechnet, gehoert nicht hierher.

Warum Funktionen und keine View-Klassen: Die Dekoratoren (`require_POST`,
`csrf_exempt`, `xframe_options_sameorigin`) stapeln sich auf Methoden nur ueber
`method_decorator`, Stapelspuren zeigen dann `dispatch` statt des Endpunkts, und
`RequestFactory` kann Funktionen unmittelbar aufrufen. Die Kapselung passiert
dort, wo Zustand ist — in den Dienstklassen.
"""
