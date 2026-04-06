/**
 * BVH Studio — Shared mutable state object.
 * All modules import state from here.
 */
import * as THREE from 'three';

export const TRACK_HEIGHT = 40;
export const HEADER_WIDTH = 120;
export const RULER_HEIGHT = 20;

export const TRACK_COLORS = {
    bvh: null,  // random
    camera: '#00bcd4',
    light: '#ffc107',
    audio: '#4caf50',
    model: '#e91e63',
};

export const TRACK_ICONS = {
    bvh: 'fa-running',
    camera: 'fa-video',
    light: 'fa-lightbulb',
    audio: 'fa-music',
    model: 'fa-user',
};

export const state = {
    renderer: null,
    scene: null,
    camera: null,
    controls: null,
    clock: new THREE.Clock(),

    project: {
        name: 'Untitled',
        fps: 30,
        tracks: [],      // Track[]
        duration: 0,     // computed from clips
    },

    selectedTrackIdx: -1,
    selectedClipIdx: -1,
    playheadFrame: 0,
    playing: false,
    playbackSpeed: 1,
    timelineZoom: 100,  // pixels per second
    timelineScrollX: 0,

    // Camera edit mode state
    cameraEditMode: false,

    // Undo suppression
    _undoSuppressed: false,
    _undoInProgress: false,
};

export const SESSION_KEY = 'bvhStudio_sessionState';
