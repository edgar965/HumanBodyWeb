// System-Stats-Polling (GPU/VRAM/Temp/CPU/RAM/Net).
// Wird von Seiten geladen die das _system_stats.html include nutzen.
// Default-Update-Interval: 2 s.
//
// Übernommen aus CamTrack (app/static/app/js/modules/system_stats.js).
// Einziger Zusatz gegenüber der Quelle: der readyState-Guard beim Auto-Start
// (siehe unten) — der Rest bleibt identisch, damit Updates aus CamTrack
// weiterhin 1:1 übernommen werden können.

const DEFAULTS = {
    endpoint:  '/api/system-stats/',
    intervalMs: 2000,
    thresholds: {
        gpu:  { warn: 70, danger: 90 },
        vram: { warn: 80, danger: 95 },
        temp: { warn: 70, danger: 80 },
        cpu:  { warn: 70, danger: 90 },
        ram:  { warn: 80, danger: 95 },
        net:  { warn: 100, danger: 500 },   // recv Mbit/s
    },
};

export class SystemStatsPoller {
    constructor(options = {}) {
        this.endpoint   = options.endpoint   || DEFAULTS.endpoint;
        this.intervalMs = options.intervalMs || DEFAULTS.intervalMs;
        this.thresholds = options.thresholds || DEFAULTS.thresholds;
        this._timer = null;
    }

    /** Idempotent — mehrfacher Aufruf startet nicht mehrere Intervals. */
    start() {
        if (this._timer) return;
        this.poll();
        this._timer = setInterval(() => this.poll(), this.intervalMs);
    }

    stop() {
        if (this._timer) {
            clearInterval(this._timer);
            this._timer = null;
        }
    }

    async poll() {
        let d;
        try {
            const r = await fetch(this.endpoint, { credentials: 'same-origin' });
            if (!r.ok) return;
            d = await r.json();
        } catch (e) {
            return;
        }
        this._renderGpu(d.gpu);
        this._renderCpu(d.cpu_percent);
        this._renderRam(d.ram_percent);
        this._renderNet(d.net_recv_mbps, d.net_sent_mbps);
    }

    _renderGpu(gpu) {
        const $ = (id) => document.getElementById(id);
        if (!gpu) {
            ['ssGpu', 'ssVram', 'ssTemp'].forEach((id) => {
                if ($(id)) $(id).textContent = 'n/a';
            });
            return;
        }
        if ($('ssGpu')) $('ssGpu').textContent = gpu.util + '%';
        this._setBar('ssGpuBar', gpu.util, this.thresholds.gpu);

        const memPct = gpu.mem_total ? Math.round(gpu.mem_used / gpu.mem_total * 100) : 0;
        const usedGb = (gpu.mem_used / 1024).toFixed(1);
        const totalGb = (gpu.mem_total / 1024).toFixed(0);
        if ($('ssVram')) $('ssVram').textContent = usedGb + '/' + totalGb + ' GB';
        this._setBar('ssVramBar', memPct, this.thresholds.vram);

        const tempEl = $('ssTemp');
        if (tempEl) {
            tempEl.textContent = gpu.temp + '°C';
            this._setPillState(tempEl, gpu.temp, this.thresholds.temp);
        }
    }

    _renderCpu(pct) {
        const el = document.getElementById('ssCpu');
        if (el) el.textContent = pct + '%';
        this._setBar('ssCpuBar', pct, this.thresholds.cpu);
    }

    _renderRam(pct) {
        const el = document.getElementById('ssRam');
        if (el) el.textContent = pct + '%';
        this._setBar('ssRamBar', pct, this.thresholds.ram);
    }

    _renderNet(recvMbps, sentMbps) {
        const el = document.getElementById('ssNet');
        if (!el) return;
        const recv = recvMbps ?? 0;
        const sent = sentMbps ?? 0;
        // Format kompakt: "↓42 ↑3" Mbit/s
        const fmt = (v) => v >= 100 ? Math.round(v) : (v >= 10 ? v.toFixed(0) : v.toFixed(1));
        el.textContent = '↓' + fmt(recv) + ' ↑' + fmt(sent);
        this._setPillState(el, recv, this.thresholds.net);
    }

    _setBar(id, pct, threshold) {
        const bar = document.getElementById(id);
        if (!bar) return;
        bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
        const pill = bar.closest('.ct-stat-pill');
        if (pill) this._setPillState(pill, pct, threshold);
    }

    _setPillState(elementOrChild, value, { warn, danger }) {
        const pill = elementOrChild.classList && elementOrChild.classList.contains('ct-stat-pill')
            ? elementOrChild
            : elementOrChild.closest('.ct-stat-pill');
        if (!pill) return;
        pill.classList.remove('ct-warn', 'ct-danger');
        if (value >= danger) pill.classList.add('ct-danger');
        else if (value >= warn) pill.classList.add('ct-warn');
    }
}

// Auto-Start wenn das DOM das Stats-Element enthaelt.
// Modul-Singleton damit das include-Pattern (Seite includes
// _system_stats.html + dieses Modul) ohne weiteren Boilerplate funktioniert.
let _autoPoller = null;
export function startSystemStats(options) {
    if (_autoPoller) return _autoPoller;
    _autoPoller = new SystemStatsPoller(options);
    _autoPoller.start();
    return _autoPoller;
}

// Guard: Module laufen deferred, koennen aber (z. B. bei spaetem Nachladen)
// erst nach DOMContentLoaded ausgefuehrt werden — dann feuert der Listener
// nie mehr und die Leiste bliebe auf "-" stehen.
function _autoStart() {
    if (document.getElementById('systemStats')) startSystemStats();
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _autoStart);
} else {
    _autoStart();
}
