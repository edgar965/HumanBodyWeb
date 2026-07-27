"""System-Stats-API (GPU/VRAM/Temp/CPU/RAM/Netz) für die Topbar-Leiste.

Portiert aus CamTrack (`app/views/settings_views.py: api_system_stats` +
`app/views/_shared.py: _read_gpu_stats`). Das JSON-Schema ist bewusst
identisch, damit `static/js/modules/system_stats.js` unverändert aus CamTrack
übernommen werden kann:

    {"gpu": {"name", "util", "mem_used", "mem_total", "temp"} | null,
     "cpu_percent", "ram_percent", "net_recv_mbps", "net_sent_mbps"}

GPU-Werte kommen von `nvidia-smi` (kein pynvml-Zwang), CPU/RAM/Netz von psutil.
"""

import logging
import subprocess
import time

from django.http import JsonResponse

logger = logging.getLogger('core')


class SystemStatsReader:
    """Liest Hardware-Auslastung und cacht sie kurz.

    Der Cache ist Prozess-global (Klassenattribut), damit mehrere offene Tabs
    nicht jeweils `nvidia-smi` starten und `psutil.cpu_percent()` blockieren —
    die Leiste pollt im Sekundentakt pro Tab.
    """

    #: Antwort so lange wiederverwenden (Sekunden). Die Leiste pollt alle 2 s.
    CACHE_TTL = 1.0

    #: Messfenster für die CPU-Auslastung. Blockiert den Request so lange.
    CPU_INTERVAL = 0.3

    #: nvidia-smi darf nicht hängen — sonst blockiert es den Worker.
    NVIDIA_SMI_TIMEOUT = 2

    _cache = {'ts': 0.0, 'data': None, 'net_prev': None}

    def read(self):
        """Liefert das Stats-Dict — aus dem Cache, wenn frisch genug."""
        now = time.time()
        if self._cache['data'] and now - self._cache['ts'] < self.CACHE_TTL:
            return self._cache['data']

        data = {
            'gpu': self.read_gpu(),
            'cpu_percent': self._cpu_percent(),
            'ram_percent': self._ram_percent(),
        }
        data.update(self._net_mbps(now))

        self._cache['ts'] = now
        self._cache['data'] = data
        return data

    def read_gpu(self):
        """GPU-Werte via nvidia-smi. None, wenn keine NVIDIA-GPU erreichbar."""
        try:
            result = subprocess.run(
                ['nvidia-smi',
                 '--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=self.NVIDIA_SMI_TIMEOUT,
            )
            if result.returncode != 0:
                return None
            line = (result.stdout or '').strip().splitlines()[0]
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 5:
                return None
            return {
                'name': parts[0],
                'util': int(parts[1]),
                'mem_used': int(parts[2]),      # MiB
                'mem_total': int(parts[3]),     # MiB
                'temp': int(parts[4]),          # °C
            }
        except (subprocess.TimeoutExpired, OSError, ValueError, IndexError) as exc:
            logger.debug('nvidia-smi nicht auswertbar: %s', exc)
            return None

    def _cpu_percent(self):
        import psutil
        return round(psutil.cpu_percent(interval=self.CPU_INTERVAL), 1)

    def _ram_percent(self):
        import psutil
        return round(psutil.virtual_memory().percent, 1)

    def _net_mbps(self, now):
        """Durchsatz aus der Differenz zum vorherigen Sample (alle Interfaces).

        Beim ersten Aufruf gibt es kein Vorgänger-Sample → 0.
        """
        import psutil
        net = psutil.net_io_counters()
        prev = self._cache.get('net_prev')
        recv = sent = 0.0
        if prev:
            dt = now - prev['ts']
            if dt > 0:
                recv = round((net.bytes_recv - prev['recv']) * 8 / 1_000_000 / dt, 1)
                sent = round((net.bytes_sent - prev['sent']) * 8 / 1_000_000 / dt, 1)
        self._cache['net_prev'] = {'ts': now, 'recv': net.bytes_recv, 'sent': net.bytes_sent}
        return {'net_recv_mbps': recv, 'net_sent_mbps': sent}


_reader = SystemStatsReader()


def api_system_stats(request):
    """GET /api/system-stats/ — Auslastung als JSON für die Topbar-Leiste."""
    return JsonResponse(_reader.read())
