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
                  ('use_dpvo', None, '--use_dpvo'),
                  ('verbose', None, '--verbose')),
        'wham': (('local_only', 'wham_estimate_local_only', '--estimate_local_only'),
                 ('smplify', 'wham_run_smplify', '--run_smplify')),
        'prompthmr': (('static_cam', 'prompthmr_static_camera', '--static_camera'),),
        # GEM-SMPL (11.09.2026): feste Kamera wie GVHMR, dazu die Demo-Videos.
        'gem': (('static_cam', 'gem_static_cam', '--static_cam'),
                ('render', None, '--render')),
        # DuoMo (12.09.2026): keine Einstellung dahinter — das Formular
        # schickt `duomo_static_cam` (Vorgabe an); DuoMo ist ohne Kamerabahn
        # ohnehin fest.
        'duomo': (('static_cam', None, '--static_cam'),),
    }

    #: Pipelines, die Glaettung und Gelenkgrenzen von `Bvhbau` kennen.
    MIT_GLAETTUNG = ('gvhmr', 'gem', 'duomo')

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
        """Die Brennweite — nur GVHMR nimmt sie entgegen."""
        s, p = self.einstellungen, self.params
        return ['--focal_length_mm',
                str(p.get('focal_length_mm', s.gvhmr_focal_length_mm))]

    def _glaettung(self):
        """Glaettung und der umgekehrte Gelenkgrenzen-Schalter (GVHMR, GEM)."""
        p = self.params
        werte = ['--smooth_sigma', str(p.get('smooth_sigma', 2.0))]
        if not p.get('joint_limits', True):
            werte.append('--no_joint_limits')
        return werte
