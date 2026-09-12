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
        # SMPL-X, die eigene Pipeline (12.09.2026): der Koerper ist GEM-SMPL,
        # also gelten GEMs Einstellungen (`EINSTELLUNGSNAME`); Finger und
        # Gesicht bekommen eigene Glaettungen ueber `_smplx_werte`.
        'smplx': (('static_cam', 'gem_static_cam', '--static_cam'),),
    }

    #: Pipelines, die Glaettung und Gelenkgrenzen von `Bvhbau` kennen.
    MIT_GLAETTUNG = ('gvhmr', 'gem', 'duomo', 'gemx', 'smplx')

    #: Pipeline -> Name, unter dem ihre Einstellungen im Modell stehen, wo er
    #: vom Pipelinenamen abweicht. SMPL-X faehrt GEMs Koerper und nimmt dessen
    #: Felder — ein eigener Feldsatz waere eine Migration fuer dieselben Werte.
    EINSTELLUNGSNAME = {'smplx': 'gem'}

    #: Glaettung der je Bild geschaetzten Teile (Finger, Kiefer, Ausdruck) in
    #: Bildern — dieselbe Vorgabe wie die Koerperglaettung von `Bvhbau`.
    SMPLX_HAND_SIGMA = 2.0
    SMPLX_FACE_SIGMA = 2.0
    #: Die Quellen der eigenen Pipeline (12.09.2026, Edgar: „in der pipeline
    #: fehlen die Haende und das Gesicht"): Koerper, Haende, Gesicht,
    #: Handgelenk — jede Stufe waehlbar, die Werte kennt `Smplxlauf`.
    #: Haende aus GEM-X: Sichtprobe auf fuenf Bildern — SMPLest-X beugt die
    #: Finger zur Faust, wo das Video sie offen zeigt; GEM-X zeigt sie offen
    #: und zittert weniger (0,007 gegen 0,009 cm/Bild^2 im Handgelenkrahmen).
    #: Die Karte faellt auf SMPLest-X zurueck, wo GEM-X nicht installiert ist.
    SMPLX_QUELLEN = {'body_source': 'gem', 'hands_source': 'gemx',
                     'face_source': 'smplestx', 'wrist_source': 'hand'}
    #: Die beiden Zugaben: Bodenkontakt der Wurzel, Netz-Video ueber dem Original.
    SMPLX_ZUGABEN = {'ground': '--no_ground', 'video': '--no_video'}

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
        if self.job.pipeline == 'smplx':
            teile += self._smplx_werte()
        return teile

    @classmethod
    def einstellungsname(cls, pipeline):
        """Der Vorsatz der Einstellungsfelder dieser Pipeline."""
        return cls.EINSTELLUNGSNAME.get(pipeline, pipeline)

    def _smplx_werte(self):
        """Finger- und Gesichtsglaettung, die vier Quellen und die zwei
        Zugaben — nur der Auftrag, sonst die Vorgabe."""
        p = self.params
        werte = ['--hand_sigma', str(p.get('hand_sigma', self.SMPLX_HAND_SIGMA)),
                 '--face_sigma', str(p.get('face_sigma', self.SMPLX_FACE_SIGMA))]
        for name, vorgabe in self.SMPLX_QUELLEN.items():
            werte += ['--' + name, str(p.get(name, vorgabe))]
        for name, schalter in self.SMPLX_ZUGABEN.items():
            if not p.get(name, True):
                werte.append(schalter)
        return werte

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
        s, p = self.einstellungen, self.params
        name = self.einstellungsname(self.job.pipeline)
        sigma = p.get('smooth_sigma', getattr(s, name + '_smooth_sigma'))
        werte = ['--smooth_sigma', str(sigma)]
        grenzen = getattr(s, name + '_joint_limits', True)
        if not p.get('joint_limits', grenzen):
            werte.append('--no_joint_limits')
        return werte
