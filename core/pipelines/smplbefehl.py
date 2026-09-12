# -*- coding: utf-8 -*-
"""Smplbefehl — die Kommandozeile für `lift_3d.py` je SMPL-Pipeline.

Herausgelöst aus `smpllauf._run_smpl_pipeline` (95 Zeilen). Der Aufbau des
Befehls war der längste Teil und der einzige, der ohne Grafikkarte prüfbar ist:
Vier Pipelines mit je eigenen Schaltern, jeder Wert entweder aus dem Auftrag oder
aus den Einstellungen.

DIE REGEL, DIE ÜBERALL GILT
===========================
Der Auftrag schlägt die Einstellung: `p.get(<schlüssel>, <einstellung>)`. Wer im
Formular etwas anderes wählt als in den Einstellungen steht, soll das auch
bekommen — sonst rechnet die Pipeline etwas anderes, als auf dem Bildschirm
stand.

`--no_joint_limits` ist der eine umgekehrte Schalter: Gelenkgrenzen sind AN, der
Schalter schaltet sie AUS. Deshalb `if not p.get('joint_limits', True)`.
"""


class Smplbefehl:
    """Baut die Argumentliste für den Wrapper — je Pipeline ihre Schalter."""

    #: Reine Ja/Nein-Schalter: (Auftragsschlüssel, Einstellungsfeld, Argument).
    #: `None` als Feld heißt: nur der Auftrag entscheidet, Vorgabe aus.
    SCHALTER = {
        'gvhmr': (('static_cam', 'gvhmr_static_cam', '--static_cam'),
                  ('use_dpvo', 'gvhmr_use_dpvo', '--use_dpvo'),
                  ('verbose', 'gvhmr_verbose', '--verbose')),
        'wham': (('local_only', 'wham_estimate_local_only', '--estimate_local_only'),
                 ('smplify', 'wham_run_smplify', '--run_smplify')),
        'prompthmr': (('static_cam', 'prompthmr_static_camera', '--static_camera'),),
        # GEM-SMPL (11.09.2026): feste Kamera wie GVHMR, dazu die Demo-Videos.
        'gem': (('static_cam', 'gem_static_cam', '--static_cam'),
                ('render', 'gem_render', '--render')),
        # DuoMo (12.09.2026): ohne Kamerabahn ohnehin fest; die Einstellung
        # ist die Vorgabe der Karte.
        'duomo': (('static_cam', 'duomo_static_cam', '--static_cam'),),
        # GEM-X (12.09.2026): wie GEM-SMPL ohne Rendern; Glaettung ueber
        # `_glaettung`, die Gelenkgrenzen nimmt der Wrapper an und ignoriert sie.
        'gemx': (('static_cam', 'gemx_static_cam', '--static_cam'),),
    }

    #: Pipelines, die Glaettung und Gelenkgrenzen von `Bvhbau` kennen.
    MIT_GLAETTUNG = ('gvhmr', 'gem', 'duomo', 'gemx')

    def __init__(self, job, einstellungen):
        self.job = job
        self.einstellungen = einstellungen
        self.params = job.pipeline_params or {}

    def bauen(self, wrapper, video, ziel):
        from django.conf import settings
        befehl = [
            settings.PIPELINE_PYTHON, str(wrapper),
            '--pipeline', self.job.pipeline,
            '--video', str(video),
            '--output', str(ziel),
            '--device', self.geraet(),
        ]
        return befehl + self.zusatz()

    def geraet(self):
        return self.params.get('device', self.einstellungen.smpl_device)

    def zusatz(self):
        """Die pipeline-eigenen Argumente."""
        teile = list(self._schalter())
        if self.job.pipeline == 'gvhmr':
            teile += self._gvhmr_werte()
        if self.job.pipeline in self.MIT_GLAETTUNG:
            teile += self._glaettung()
        return teile

    def _schalter(self):
        for schluessel, feld, argument in self.SCHALTER.get(self.job.pipeline, ()):
            vorgabe = (getattr(self.einstellungen, feld) if feld else False)
            if self.params.get(schluessel, vorgabe):
                yield argument

    def _gvhmr_werte(self):
        """Die Brennweite — nur GVHMR nimmt sie entgegen — und der
        umgekehrte Render-Schalter: Das Demo rendert von sich aus, `--no_render`
        laesst die drei Videos weg (12.09.2026)."""
        s, p = self.einstellungen, self.params
        werte = ['--focal_length_mm',
                 str(p.get('focal_length_mm', s.gvhmr_focal_length_mm))]
        if not p.get('render', s.gvhmr_render):
            werte.append('--no_render')
        return werte

    def _glaettung(self):
        """Glaettung und der umgekehrte Gelenkgrenzen-Schalter.

        Rueckfall sind die Einstellungen der Pipeline (`gvhmr_smooth_sigma`,
        `duomo_joint_limits`, …, seit 12.09.2026) — ohne stille Vorgabe:
        Fehlt das Feld, fliegt der AttributeError, den der Waechter in
        `test_smplbefehl` vorher findet. GEM-X hat keine Gelenkgrenzen.
        """
        s, p, name = self.einstellungen, self.params, self.job.pipeline
        sigma = p.get('smooth_sigma', getattr(s, name + '_smooth_sigma'))
        werte = ['--smooth_sigma', str(sigma)]
        grenzen = getattr(s, name + '_joint_limits', True)
        if not p.get('joint_limits', grenzen):
            werte.append('--no_joint_limits')
        return werte
