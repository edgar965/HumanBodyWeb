# -*- coding: utf-8 -*-
"""Webserveralternativen — ASGI-Server im Vergleich zu Daphne.

Die Tabelle der Seite „Hilfe → Architektur → Webserver" (Edgar,
23.09.2026: „mach mir einen Vergleich … Verbreitung, Wartbarkeit, Open
Source, Vor- und Nachteile, deine Empfehlung" — Anlass: die Frage, ob ein
anderer Server HTTP/2 bringt und die Ladezeit der Szene senkt, siehe
`studio.md`/`szene.md`, „texturbuendel").

**Vorher falsch behauptet, hier richtiggestellt:** Ich hatte Edgar gesagt,
Daphne könne kein HTTP/2. Stimmt nicht — Daphne terminiert HTTP/2 nativ,
aber NUR mit TLS und den Twisted-Extras `pip install "Twisted[tls,http2]"`
(`h2`, `priority`). Geprüft (23.09.2026): `Twisted` 25.5.0 ist installiert,
`h2`/`priority` NICHT — HTTP/2 ist also technisch erreichbar, aber noch
nicht eingerichtet, und JEDE Umstellung auf HTTP/2 bräuchte ohnehin TLS
(Chrome verhandelt h2 nur über https) — mit allen Folgen für `localStorage`
(eigene Herkunft, `szene.md`: Reiterstände, Kategorien, GarmentCode-
Gedächtnis stünden auf `https://` leer).

ZAHLEN UND QUELLEN (gemessen 23.09.2026, `gh api repos/<repo>` und
PyPI-JSON — keine Schätzung)
=============================================================
`sterne`: GitHub-Sterne des Repos (`stargazers_count`) — ein grober, aber
nachprüfbarer Verbreitungs-Näherungswert, keine Download-Zahl (die liefert
GitHub nicht; PyPI-Downloads sind bei ASGI-Servern durch transitive
Abhängigkeiten stark verzerrt, z. B. zieht jedes FastAPI-Tutorial Uvicorn).
`tage_still`: Tage zwischen dem letzten Push (`pushed_at`) und dem
23.09.2026 — je kleiner, desto frischer gepflegt. Beides ändert sich mit
der Zeit; wer die Seite später liest, sieht das Datum in `STAND`.
"""

STAND = '23.09.2026'

__all__ = ['Webserveralternativen']


class Webserveralternativen:
    """Die Vergleichszeilen, roh — die Vorlage/View rechnet nichts dazu."""

    #: Aktueller Server dieses Projekts (`ui/asgi.py`, `start_server.ps1`).
    AKTUELLER = 'daphne'

    ZEILEN = [
        {
            'kennung': 'daphne', 'name': 'Daphne', 'aktuell': True,
            'sterne': 2687, 'tage_still': 26, 'lizenz': 'BSD-3-Clause',
            'http2': 'Mit TLS + Twisted-Extras (`h2`, `priority`) — hier noch nicht installiert',
            'websocket': 'Ja — Referenzserver für Django Channels',
            'vorteile': 'Von Django/Channels selbst gepflegt, genau die Kombination, '
                        'die dieses Projekt schon einsetzt; keine Umstellung nötig.',
            'nachteile': 'Kleinstes Projekt der vier (2.687 Sterne), HTTP/2 ist ein '
                         'Nebenzweig von Twisted, nicht der Kernfokus des Projekts.',
            'empfehlung': 'Bleiben — HTTP/2 hier nur mit TLS aktivieren, wenn Edgar den '
                           'Herkunftswechsel (https, localStorage leer) ausdrücklich will.',
        },
        {
            'kennung': 'uvicorn', 'name': 'Uvicorn', 'aktuell': False,
            'sterne': 10979, 'tage_still': 1, 'lizenz': 'BSD-3-Clause',
            'http2': 'Nein — nur über einen vorgeschalteten Reverse-Proxy (nginx, Caddy)',
            'websocket': 'Ja (websockets/wsproto) — von den Channels-Dokumenten offiziell '
                         'als Option genannt',
            'vorteile': 'Am weitesten verbreitet, sehr aktiv gepflegt (letzter Push: '
                        'gestern), in Benchmarks meist die schnellste der vier für reines '
                        'HTTP/WebSocket.',
            'nachteile': 'Bringt KEIN HTTP/2 — würde die eigentliche Frage (weniger '
                         'Verbindungswellen) gar nicht lösen, ohne zusätzlich einen Proxy '
                         'aufzusetzen.',
            'empfehlung': 'Nicht der richtige Griff für „HTTP/2" — dafür bräuchte es ohnehin '
                           'denselben Proxy wie bei Daphne.',
        },
        {
            'kennung': 'hypercorn', 'name': 'Hypercorn', 'aktuell': False,
            'sterne': 1611, 'tage_still': 319, 'lizenz': 'MIT',
            'http2': 'Ja, nativ — HTTP/1, HTTP/2, HTTP/3 (QUIC) und WebSocket in einem Prozess',
            'websocket': 'Ja — von den Channels-Dokumenten selbst als Alternative zu Daphne genannt',
            'vorteile': 'Protokoll-vollständigster Server der vier (auch HTTP/3); als ASGI-'
                        'Anwendung derselbe Einstiegspunkt wie Daphne (`ui.asgi:application`) — '
                        'kleinster Umstellungsaufwand für dieses Projekt.',
            'nachteile': 'Letzter Push vor 319 Tagen (Stand 23.09.2026) — spürbar ruhiger '
                         'gepflegt als die anderen drei, kleinste Sternezahl.',
            'empfehlung': 'Die naheliegende Wahl, WENN Edgar echtes HTTP/2 will — braucht '
                           'trotzdem TLS und damit den Herkunftswechsel.',
        },
        {
            'kennung': 'granian', 'name': 'Granian', 'aktuell': False,
            'sterne': 5665, 'tage_still': 9, 'lizenz': 'BSD-3-Clause',
            'http2': 'Ja, nativ (Rust-Implementierung, inkl. TLS)',
            'websocket': 'Eingeschränkt — gemeldete Aussetzer mit Django-Channels-WebSockets '
                         '(„RuntimeError: ASGI flow error"); die Channels-Dokumentation nennt '
                         'Daphne, nicht Granian, als offiziell unterstützt',
            'vorteile': 'Rust-Kern, sehr aktiv gepflegt (Push vor 9 Tagen), zweitmeiste '
                        'Sterne — spürbar wachsende Verbreitung.',
            'nachteile': 'WebSocket/Lifespan-Unterstützung laut eigenen Melde-Issues noch '
                         'lückenhaft — genau die Kombination (Channels, `core/consumers.py`, '
                         'Pipeline-Fortschritt über WebSocket), auf der dieses Projekt steht.',
            'empfehlung': 'Nicht jetzt — erst wenn die Channels-WebSocket-Lücken belegt '
                          'geschlossen sind. Vielversprechend, aber ein Risiko für die '
                          'Pipeline-Fortschrittsanzeige, kein Performance-Vorteil, der das '
                          'aufwiegt.',
        },
        {
            'kennung': 'gunicorn', 'name': 'Gunicorn + Uvicorn-Worker', 'aktuell': False,
            'sterne': 10680, 'tage_still': 17, 'lizenz': 'MIT',
            'http2': 'Nein — Gunicorn selbst spricht nur WSGI/HTTP1, die Worker sind Uvicorn',
            'websocket': 'Ja, über die Uvicorn-Worker',
            'vorteile': 'Bewährte Prozessverwaltung (Worker-Neustart, graceful reload) — '
                        'stark in klassischen Multi-Worker-Produktivumgebungen.',
            'nachteile': 'Löst die HTTP/2-Frage nicht (siehe Uvicorn); für einen einzelnen '
                         'Dev-Server ohne mehrere Worker kein Vorteil gegenüber Daphne.',
            'empfehlung': 'Für dieses Projekt kein Thema — passt zu einer Multi-Worker-'
                           'Produktivbereitstellung, nicht zu `restart_server.py`/Autostart.',
        },
    ]

    @classmethod
    def zeilen(cls):
        """Zeilen mit Rang nach Sternen (absteigend) — Vergleichsgröße für die Spalte."""
        geordnet = sorted(cls.ZEILEN, key=lambda z: -z['sterne'])
        return [dict(z, rang=i + 1) for i, z in enumerate(geordnet)]
