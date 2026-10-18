# -*- coding: utf-8 -*-
"""Mesh3daigpuprozesse — GPU-Auslastung und GPU-Speicher JE PROZESS aus den Windows-Leistungszählern (18.10.2026, Reiter „Lauf Aktuell“ auf /mesh-3D-AI/).

nvidia-smi meldet unter Windows (WDDM) je Prozess nur „[N/A]“ (gemessen 18.10.2026: `--query-compute-apps=pid,used_memory`). Die Zähler, aus denen der Task-Manager seine Spalten
„GPU“ und „Dedizierter GPU-Speicher“ liest, liefern beides (`ProjektTemp/_wegwerf/lauf_aktuell_probe4.py`: 852 Engine-Instanzen, die MIA-Arbeiter mit je 6.866 MB):
  \\GPU Engine(pid_<pid>_luid_…_eng_<n>_engtype_<Art>)\\Utilization Percentage   — ein Ratenzähler: Mittel seit der vorigen Abfrage;
  \\GPU Process Memory(pid_<pid>_luid_…)\\Dedicated Usage                          — Bytes.
Je Prozess wird je Engine-Art summiert; „Auslastung“ ist wie im Task-Manager die größte Art. Die Abfrage bleibt offen, damit jede Messung das Mittel seit der vorigen ist; liegt die vorige
länger als `FRISCH_S` zurück, wird zweimal im Abstand von `WARTE_S` gemessen (ein Mittel über eine Stunde Ruhe wäre keine Auslastung). Ohne pywin32 oder bei einem Fehler: `{}`.

    Mesh3daigpuprozesse.lesen() -> {pid: {'prozent': float, 'arten': {Art: float}, 'mb': float}}
"""

import logging
import re
import threading
import time

logger = logging.getLogger('core')

__all__ = ['Mesh3daigpuprozesse']


class Mesh3daigpuprozesse:
    AUSLASTUNG = r'\GPU Engine(*)\Utilization Percentage'
    SPEICHER = r'\GPU Process Memory(*)\Dedicated Usage'
    ENGINE = re.compile(r'^pid_(\d+)_.*_engtype_(.+)$')
    PID = re.compile(r'^pid_(\d+)_')
    FRISCH_S = 30.0
    WARTE_S = 0.5
    _sperre = threading.Lock()
    _abfrage = None
    _zuletzt = 0.0

    @classmethod
    def lesen(cls):
        try:
            import pywintypes
            import win32pdh
        except ImportError:
            return {}
        with cls._sperre:
            try:
                if cls._abfrage is None:
                    q = win32pdh.OpenQuery()
                    cls._abfrage = (q, win32pdh.AddEnglishCounter(q, cls.AUSLASTUNG), win32pdh.AddEnglishCounter(q, cls.SPEICHER))
                    cls._zuletzt = 0.0
                q, z_last, z_mb = cls._abfrage
                if time.time() - cls._zuletzt > cls.FRISCH_S:
                    win32pdh.CollectQueryData(q)
                    time.sleep(cls.WARTE_S)
                win32pdh.CollectQueryData(q)
                cls._zuletzt = time.time()
                last = win32pdh.GetFormattedCounterArray(z_last, win32pdh.PDH_FMT_DOUBLE)
                mb = win32pdh.GetFormattedCounterArray(z_mb, win32pdh.PDH_FMT_LARGE)
            except pywintypes.error as f:
                logger.warning('Mesh3daigpuprozesse: Leistungszähler nicht lesbar (%s) — Abfrage wird neu angelegt', f)
                cls._schliessen()
                return {}
        return cls.auswerten(last, mb)

    @classmethod
    def auswerten(cls, last, mb):
        """Aus den Zählerständen `{Instanz: Wert}` die Werte je pid."""
        aus = {}
        for name, wert in last.items():
            m = cls.ENGINE.match(name)
            if m and wert > 0:
                arten = aus.setdefault(int(m.group(1)), {'prozent': 0.0, 'arten': {}, 'mb': 0.0})['arten']
                arten[m.group(2)] = arten.get(m.group(2), 0.0) + float(wert)
        for name, wert in mb.items():
            m = cls.PID.match(name)
            if m:
                aus.setdefault(int(m.group(1)), {'prozent': 0.0, 'arten': {}, 'mb': 0.0})['mb'] += float(wert) / 1e6
        for werte in aus.values():
            werte['prozent'] = min(100.0, max(werte['arten'].values(), default=0.0))
        return aus

    @classmethod
    def _schliessen(cls):
        try:
            import win32pdh
            if cls._abfrage is not None:
                win32pdh.CloseQuery(cls._abfrage[0])
        except Exception:  # noqa: BLE001 — Aufräumen nach einem Fehler darf selbst nicht scheitern
            pass
        cls._abfrage = None
