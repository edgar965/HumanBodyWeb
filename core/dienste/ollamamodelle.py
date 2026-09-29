# -*- coding: utf-8 -*-
"""Ollamamodelle — die lokal installierten Modelle, die Bilder lesen können, und ein Aufruf mit Bild.

Edgar (29.09.2026): „warum kannst du den API Aufruf nicht mit einer lokalen KI machen? Ich habe doch um die 10
gute lokale KIs installiert" — die Prüf-KI des Kostüm-Kreislaufs läuft über Ollama auf DIESEM Rechner, ohne
Cloud. Welche Modelle Bilder verstehen, sagt Ollama selbst (`/api/show` → `capabilities` enthält `vision`),
nicht eine Namensliste. Angezeigt wird jedes mit Fassung und Dateigröße (Regel `modellnamen-genau`: der
Ollama-Name der Q4-Fassung trägt kein Suffix). Adresse `127.0.0.1`, nie `localhost` (IPv6-Umweg unter Windows,
`zeit-messen.md`).
"""

import json
import logging
import urllib.error
import urllib.request

__all__ = ['Ollamamodelle']

logger = logging.getLogger('core')


class Ollamamodelle:
    ADRESSE = 'http://127.0.0.1:11434'

    @classmethod
    def _holen(cls, pfad, daten=None, zeitlimit=5.0):
        anfrage = urllib.request.Request(
            cls.ADRESSE + pfad,
            data=json.dumps(daten).encode('utf-8') if daten is not None else None,
            headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(anfrage, timeout=zeitlimit) as antwort:
            return json.load(antwort)

    @classmethod
    def mit_bildern(cls, zeitlimit=3.0):
        """[(name, anzeige)] aller installierten Modelle mit Fähigkeit `vision` — leer, wenn Ollama nicht
        antwortet."""
        try:
            modelle = cls._holen('/api/tags', zeitlimit=zeitlimit).get('models') or []
            aus = []
            for m in modelle:
                info = cls._holen('/api/show', {'model': m['name']}, zeitlimit=zeitlimit)
                if 'vision' not in (info.get('capabilities') or []):
                    continue
                d = m.get('details') or {}
                aus.append(
                    (
                        m['name'],
                        '%s (%s, %s, %.1f GB Datei)'
                        % (
                            m['name'],
                            d.get('quantization_level', '?'),
                            d.get('parameter_size', '?'),
                            m.get('size', 0) / 1e9,
                        ),
                    )
                )
            return sorted(aus)
        except (urllib.error.URLError, OSError, ValueError) as fehler:
            logger.warning('Ollama nicht erreichbar (%s): keine Prüf-KI zur Auswahl', fehler)
            return []

    @classmethod
    def fragen(cls, modell, text, bilder_b64, schema, zeitlimit=900.0):
        """Eine Frage mit Bildern; die Antwort ist JSON nach `schema` (Ollama `format`). → dict."""
        daten = {
            'model': modell,
            'messages': [{'role': 'user', 'content': text, 'images': list(bilder_b64)}],
            'stream': False,
            'format': schema,
            'think': False,
            'keep_alive': '10m',
            'options': {'temperature': 0.2, 'num_ctx': 16384},
        }
        antwort = cls._holen('/api/chat', daten, zeitlimit=zeitlimit)
        inhalt = (antwort.get('message') or {}).get('content') or ''
        return json.loads(inhalt), {
            k: antwort.get(k) for k in ('total_duration', 'eval_count', 'prompt_eval_count')
        }
