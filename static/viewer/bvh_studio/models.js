/**
 * BVH Studio — Timeline, Track, and Clip classes.
 */
import * as THREE from 'three';
import { state } from './state.js';

// =========================================================================
// Timeline — top-level container for the project timeline.
// Manages typed track lists and provides computed duration.
// =========================================================================
export class Timeline {
    constructor() {
        this.name = 'Untitled';
        this.fps = 30;
        this._allTracks = [];

        // Project-level settings (set from preferences)
        this.defaultModel = 'Rig2';
        this.defaultBodyType = 'Female_Caucasian';
        this.videoOutputPath = '';
        this.bvhOutputPath = '';
        this.projectPath = '';

        // Shared AudioContext for all audio tracks
        this._audioCtx = null;
        this._lastSavePath = null;
    }

    // ----- Flat track array (backward-compatible) -----
    get tracks() { return this._allTracks; }
    set tracks(arr) { this._allTracks = Array.isArray(arr) ? arr : []; }

    // ----- Typed views -----
    get animations()   { return this._allTracks.filter(t => t.type === 'bvh'); }
    get audioTracks()  { return this._allTracks.filter(t => t.type === 'audio'); }
    get modelTracks()  { return this._allTracks.filter(t => t.type === 'model'); }
    get cameraTracks() { return this._allTracks.filter(t => t.type === 'camera'); }
    get lightTracks()  { return this._allTracks.filter(t => t.type === 'light'); }

    // ----- Computed duration (seconds) -----
    get duration() {
        let maxEnd = 0;
        for (const track of this._allTracks) {
            for (const clip of track.clips) {
                const end = clip.endFrame / this.fps;
                if (end > maxEnd) maxEnd = end;
            }
        }
        return maxEnd;
    }
    set duration(_v) { /* computed — noop */ }

    // ----- Track management -----
    addTrack(track) {
        this._allTracks.push(track);
        return track;
    }

    insertTrackAfter(refTrack, newTrack) {
        const idx = this._allTracks.indexOf(refTrack);
        if (idx >= 0) {
            this._allTracks.splice(idx + 1, 0, newTrack);
        } else {
            this._allTracks.push(newTrack);
        }
        return newTrack;
    }

    removeTrackAt(idx) {
        if (idx < 0 || idx >= this._allTracks.length) return null;
        const removed = this._allTracks.splice(idx, 1)[0];
        // Fix _linkedAnimIdx references on model tracks
        for (const t of this._allTracks) {
            if (t.type === 'model' && t._linkedAnimIdx >= 0) {
                if (t._linkedAnimIdx === idx) t._linkedAnimIdx = -1;
                else if (t._linkedAnimIdx > idx) t._linkedAnimIdx--;
            }
        }
        return removed;
    }

    clear() {
        this._allTracks.length = 0;
    }

    indexOf(track) {
        return this._allTracks.indexOf(track);
    }

    // Resolve linked animation track for a model track
    getLinkedAnimation(modelTrack) {
        const idx = modelTrack._linkedAnimIdx;
        if (idx < 0 || idx >= this._allTracks.length) return null;
        const t = this._allTracks[idx];
        return (t && t.type === 'bvh') ? t : null;
    }
}

// =========================================================================
// Track — a single lane in the timeline (animation, camera, light, audio, model).
// =========================================================================
export class Track {
    constructor(name, preset = 'FemaleGarment', bodyType = 'Female_Caucasian') {
        this.name = name;
        this.type = 'bvh';       // 'bvh' | 'camera' | 'light' | 'audio' | 'model'
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

// =========================================================================
// Clip — a single item on a track (animation clip, keyframe, audio segment, model preset).
// =========================================================================
export class Clip {
    constructor(category, name, totalFrames, fps) {
        this.type = 'bvh';      // 'bvh' | 'camera_kf' | 'light_kf' | 'audio' | 'model'
        this.category = category;
        this.name = name;
        this.totalFrames = totalFrames;
        this.fps = fps || 30;
        this.startFrame = 0;     // position on timeline (in project fps)
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
