# -*- coding: utf-8 -*-
"""Mesh3dailaufprozesse — die rechnenden Prozesse von Mesh3D-AI mit CPU, Arbeitsspeicher und GPU je Prozessbaum (18.10.2026, Reiter „Lauf Aktuell“ auf /mesh-3D-AI/).

Ein Job ist ein Python-Prozess, dessen Befehlszeile „mesh3dai“ enthält (die Skripte unter `ProjektTemp/_wegwerf/mesh3dai_*.py`) und dessen Elternprozess KEIN solcher ist — der venv-Starter
(`python14\\Scripts\\python.exe`, ~4 MB) und der echte Interpreter darunter sind ein Job, die MIA-Arbeiter darunter (`python11_mia`, `mesh3dai_mia_stapel.py`) gehören zu ihm. Gezählt wird der ganze
Baum: CPU als Kerne (Δ CPU-Sekunden / Δ Zeit seit der vorigen Messung; ohne frische vorige zweimal im Abstand von `WARTE_S`), Arbeitsspeicher (RSS), GPU aus `Mesh3daigpuprozesse`.

Ketten: Git-Bash-Prozesse `bash.exe <name>.sh` mit „mesh3dai“ im Namen. Git-Bash trennt beim Start eines Kindes die Windows-Elternkette (gemessen 18.10.2026: der Elternprozess von
`mesh3dai_formen_daten_v9.sh` lebt nicht mehr, obwohl `mesh3dai_formen_nach_tests.sh` ihn gestartet hat) — ob eine Kette wartet oder gerade einen Schritt ausführt, ist darum nicht sicher zu
sagen; sicher ist nur „führt diesen Job aus“, wenn sie ein Vorfahr des Jobs ist. Zwei Ketten mit demselben Skript laufen doppelt (so gefunden 18.10.2026: eine verwaiste Paarkette von 20:18).

Die Elternkarte kommt in EINEM Zug aus `psutil._psplatform.ppid_map()` (0,17 s für 531 Prozesse); `process_iter(['ppid'])` holt sie unter Windows je Prozess neu — gemessen 101 s.

    Mesh3dailaufprozesse.lesen(gpu) -> {'jobs': [...], 'ketten': [...], 'fremde_gpu': [...], 'kerne': int}
"""

import logging
import os
import threading
import time

import psutil

logger = logging.getLogger('core')

__all__ = ['Mesh3dailaufprozesse']


class Mesh3dailaufprozesse:
    MERKMAL = 'mesh3dai'
    FRISCH_S = 30.0
    WARTE_S = 0.5
    #: andere Programme auf der GPU erst ab hier nennen (MB oder Prozent)
    FREMD_MB, FREMD_PROZENT = 200.0, 1.0
    _sperre = threading.Lock()
    _vorher = {}
    _vorher_zeit = 0.0

    @classmethod
    def lesen(cls, gpu=None):
        gpu = gpu or {}
        karte = cls._elternkarte()
        kinder = {}
        for pid, eltern in karte.items():
            kinder.setdefault(eltern, []).append(pid)
        kandidaten = cls._kandidaten()
        laeufe = {pid for pid, k in kandidaten.items() if k['python'] and cls.MERKMAL in ' '.join(k['cmd']).lower() and not cls._server(k['cmd'])}
        ketten = {pid: k for pid, k in kandidaten.items() if not k['python'] and len(k['cmd']) > 1 and k['cmd'][1].lower().endswith('.sh') and cls.MERKMAL in k['cmd'][1].lower()}
        # Eine Unter-Shell (`$(…)`, Pipe) trägt dieselbe Befehlszeile wie ihre Kette und hängt unter ihr — sie ist dieselbe Kette, keine zweite.
        ketten = {pid: k for pid, k in ketten.items() if not any(v in ketten and ketten[v]['cmd'][1] == k['cmd'][1] for v in cls._vorfahren(pid, karte))}
        spitzen = sorted((pid for pid in laeufe if karte.get(pid) not in laeufe), key=lambda pid: kandidaten[pid]['start'])
        baeume = {pid: cls._baum(pid, kinder) for pid in spitzen}
        kerne = cls._kerne([p for b in baeume.values() for p in b])
        jobs = []
        for pid in spitzen:
            k, baum = kandidaten[pid], baeume[pid]
            vorfahren = cls._vorfahren(pid, karte)
            jobs.append({**cls._befehl(k['cmd']), 'pid': pid, 'start': k['start'], 'prozesse': len(baum),
                         'kette': list(dict.fromkeys(os.path.basename(ketten[v]['cmd'][1]) for v in vorfahren if v in ketten)),
                         'cpu_kerne': round(sum(kerne.get(p, 0.0) for p in baum), 2), 'ram_mb': round(cls._ram(baum)), **cls._gpu_baum(baum, gpu)})
        ausfuehrend = {v for pid in spitzen for v in cls._vorfahren(pid, karte)}
        namen = [os.path.basename(k['cmd'][1]) for k in ketten.values()]
        kettenliste = [{'name': os.path.basename(k['cmd'][1]), 'pid': pid, 'start': k['start'], 'fuehrt_aus': pid in ausfuehrend,
                        'doppelt': namen.count(os.path.basename(k['cmd'][1])) > 1} for pid, k in sorted(ketten.items(), key=lambda x: x[1]['start'])]
        eigene = {p for b in baeume.values() for p in b}
        return {'jobs': jobs, 'ketten': kettenliste, 'fremde_gpu': cls._fremde(gpu, eigene), 'kerne': psutil.cpu_count(logical=True)}

    @staticmethod
    def _elternkarte():
        try:
            return dict(psutil._psplatform.ppid_map())
        except (AttributeError, OSError, psutil.Error) as f:
            logger.warning('Mesh3dailaufprozesse: keine Elternkarte (%s) — Jobs ohne Kindprozesse und Ketten', f)
            return {}

    @staticmethod
    def _kandidaten():
        aus = {}
        for p in psutil.process_iter(['name']):
            name = (p.info['name'] or '').lower()
            if not name.startswith(('python', 'bash')):
                continue
            try:
                aus[p.pid] = {'python': name.startswith('python'), 'cmd': p.cmdline(), 'start': p.create_time()}
            except (psutil.Error, OSError):
                continue
        return aus

    @staticmethod
    def _server(cmd):
        return any(os.path.basename(t).lower() == 'manage.py' for t in cmd)

    @staticmethod
    def _baum(pid, kinder):
        aus, offen = [], [pid]
        while offen:
            p = offen.pop()
            if p in aus:
                continue
            aus.append(p)
            offen.extend(kinder.get(p, []))
        return aus

    @staticmethod
    def _vorfahren(pid, karte, tiefe=8):
        aus, p = [], karte.get(pid)
        while p and len(aus) < tiefe and p not in aus:
            aus.append(p)
            p = karte.get(p)
        return aus

    @staticmethod
    def _befehl(cmd):
        """Skript (Dateiname des ersten `.py`), Argumente danach, Umgebung (Ordner des Interpreters unter A:\\3DTools)."""
        i = next((n for n, t in enumerate(cmd) if t.lower().endswith('.py')), None)
        umgebung = next((t for t in os.path.normpath(cmd[0]).split(os.sep) if t.lower().startswith('python')), os.path.basename(cmd[0])) if cmd else ''
        if i is None:
            return {'skript': ' '.join(cmd[1:3]), 'argumente': cmd[3:], 'umgebung': umgebung}
        return {'skript': os.path.basename(cmd[i]), 'argumente': cmd[i + 1:], 'umgebung': umgebung}

    @classmethod
    def _cpu(cls, pids):
        aus = {}
        for pid in pids:
            try:
                p = psutil.Process(pid)
                t = p.cpu_times()
                aus[(pid, p.create_time())] = t.user + t.system
            except (psutil.Error, OSError):
                continue
        return aus

    @classmethod
    def _kerne(cls, pids):
        """{pid: Kerne} — Δ CPU-Sekunden / Δ Zeit. Ein Prozess, der nach der vorigen Messung entstand, zählt ganz; einer, der vorher schon lief und nicht gemessen war, mit 0."""
        jetzt_werte = cls._cpu(pids)
        with cls._sperre:
            vorher, vorher_zeit = cls._vorher, cls._vorher_zeit
        if not vorher or time.time() - vorher_zeit > cls.FRISCH_S:
            vorher, vorher_zeit = jetzt_werte, time.time()
            time.sleep(cls.WARTE_S)
            jetzt_werte = cls._cpu(pids)
        jetzt = time.time()
        with cls._sperre:
            cls._vorher, cls._vorher_zeit = jetzt_werte, jetzt
        dauer = max(jetzt - vorher_zeit, 1e-3)
        aus = {}
        for (pid, start), sek in jetzt_werte.items():
            alt = vorher.get((pid, start), 0.0 if start >= vorher_zeit else sek)
            aus[pid] = aus.get(pid, 0.0) + max(0.0, sek - alt) / dauer
        return aus

    @staticmethod
    def _gpu_baum(baum, gpu):
        """GPU des ganzen Baums: je Engine-Art über die Prozesse summiert, Auslastung = größte Art (wie der Task-Manager je Prozess), Speicher summiert."""
        arten = {}
        for p in baum:
            for art, w in ((gpu.get(p) or {}).get('arten') or {}).items():
                arten[art] = arten.get(art, 0.0) + w
        return {'gpu_prozent': round(min(100.0, max(arten.values(), default=0.0)), 1), 'gpu_arten': {a: round(w, 1) for a, w in arten.items() if w >= 0.1},
                'gpu_mb': round(sum((gpu.get(p) or {}).get('mb', 0.0) for p in baum)), 'gpu_pids': [p for p in baum if (gpu.get(p) or {}).get('mb', 0.0) >= 1.0]}

    @staticmethod
    def _ram(pids):
        summe = 0
        for pid in pids:
            try:
                summe += psutil.Process(pid).memory_info().rss
            except (psutil.Error, OSError):
                continue
        return summe / 1e6

    @classmethod
    def _fremde(cls, gpu, eigene):
        aus = []
        for pid, w in gpu.items():
            if pid in eigene or (w['mb'] < cls.FREMD_MB and w['prozent'] < cls.FREMD_PROZENT):
                continue
            try:
                name = psutil.Process(pid).name()
            except (psutil.Error, OSError):
                name = '(beendet)'
            aus.append({'pid': pid, 'name': name, 'gpu_mb': round(w['mb']), 'gpu_prozent': round(w['prozent'], 1)})
        return sorted(aus, key=lambda x: (-x['gpu_mb'], -x['gpu_prozent']))[:10]
