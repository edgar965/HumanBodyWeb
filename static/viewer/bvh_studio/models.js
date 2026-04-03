/**
 * BVH Studio — Track and Clip classes.
 */
import * as THREE from 'three';
import { state } from './state.js';

export class Track {
    constructor(name, preset = 'FemaleGarment', bodyType = 'Female_Caucasian') {
        this.name = name;
        this.type = 'bvh';       // 'bvh' | 'camera' | 'light' | 'audio'
        this.preset = preset;
        this.bodyType = bodyType;
        this.clips = [];
        this.muted = false;
        this.color = `hsl(${Math.random() * 360}, 60%, 50%)`;
        // 3D (BVH only)
        this.mesh = null;
        this.skeleton = null;
        this.mixer = null;
        this.group = new THREE.Group();
        this.position = [0, 0, 0];
        // Camera track
        this.cameraActive = false;     // override viewport camera during playback
        this._savedCamPos = null;
        this._savedCamQuat = null;
        // Light track
        this.light = null;
        this.lightHelper = null;
        this.lightVisible = true;
        // Audio track
        this.audioCtx = null;
        this.gainNode = null;
        this.sourceNode = null;
    }
}

export class Clip {
    constructor(category, name, totalFrames, fps) {
        this.type = 'bvh';      // 'bvh' | 'camera_kf' | 'light_kf' | 'audio'
        this.category = category;
        this.name = name;
        this.totalFrames = totalFrames;
        this.fps = fps || 30;
        this.startFrame = 0;     // position on timeline
        this.trimIn = 0;         // frames trimmed from start
        this.trimOut = 0;        // frames trimmed from end
        this.speed = 1.0;
        this.smoothSigma = 0;
        this.groundFix = false;
        this.blendIn = 0;
        this.blendOut = 0;
        this.animClip = null;    // Three.js AnimationClip (retargeted)
        // Type-specific data
        this.data = {};
    }
    get duration() {
        if (this.type === 'camera_kf' || this.type === 'light_kf') return 0;
        if (this.type === 'audio') return (this.data.audioDuration || 0) / this.speed;
        return (this.totalFrames - this.trimIn - this.trimOut) / (this.fps * this.speed);
    }
    get endFrame() {
        if (this.type === 'camera_kf' || this.type === 'light_kf') return this.startFrame;
        return this.startFrame + Math.ceil(this.duration * state.project.fps);
    }
}
