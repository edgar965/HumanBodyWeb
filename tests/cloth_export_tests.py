# -*- coding: utf-8 -*-
"""Cloth Export: Endpunkt

Methodenpruefung und Engine-Auswahl von /api/cloth/export/

Aus tests/cloth_export_tests.py herausgeloest (17.08.2026): Die Datei hatte ueber 300 Zeilen und
eine Klasse mit ueber 300 — Befund `dateigroesse`. Gemeinsame Importe und
Fixtures stehen in `_cloth_basis.py`.
"""
from .base import TestCategory, Netzruf
# siehe `cloth_engine_tests`: der Aufruf setzt `sys.path` fuer `collision.*`.
from ._cloth_basis import Clothbasis


Clothbasis.pfad_sichern()


class ClothExportTests(TestCategory):
    name = 'Cloth Export: Endpunkt'
    description = 'Methodenpruefung und Engine-Auswahl von /api/cloth/export/'

    @staticmethod
    def test_cloth_export_api_rejects_http_get_method():
        """Die HTTP-Route /api/cloth/export/ akzeptiert nur POST — GET → 405."""
        code, _ = Netzruf.senden('/api/cloth/export/', method='GET')
        return code == 405, f'HTTP {code}'

    @staticmethod
    def test_cloth_export_api_rejects_unknown_engine_name():
        """POST mit engine='bogus' wird vom Dispatcher mit 400 abgelehnt."""
        code, body = Netzruf.senden('/api/cloth/export/', method='POST',
                                   data={'engine': 'bogus', 'quality': 'low'})
        if code != 400:
            return False, f'HTTP {code} body={body}'
        return True, f'HTTP {code}'

    @staticmethod
    def test_cloth_export_api_registers_all_three_engines():
        """blender_eevee / warp_blender / warp_only sind im Dispatcher eingetragen."""
        for eng in ('blender_eevee', 'warp_blender', 'warp_only'):
            code, body = Netzruf.senden('/api/cloth/export/', method='POST',
                                       data={'engine': eng, 'quality': 'low'})
            err = str(body.get('error', ''))
            if 'unknown engine' in err.lower():
                return False, f'{eng}: {err}'
        return True, 'blender_eevee, warp_blender, warp_only akzeptiert'
