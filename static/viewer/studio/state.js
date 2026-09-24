/**
 * BVH Studio — Shared mutable state object.
 * All modules import state from here.
 */
import * as THREE from 'three';
import { Timeline } from './models.js';

export const TRACK_HEIGHT = 40;
export const HEADER_WIDTH = 200;
export const RULER_HEIGHT = 20;

export const TRACK_COLORS = {
    bvh: null,  // random
    camera: '#00bcd4',
    light: '#ffc107',
    audio: '#4caf50',
    model: '#e91e63',
    mimik: '#ff8a65',
    script: '#ba68c8',
    effekte: '#26c6da',
};

export const TRACK_ICONS = {
    bvh: 'fa-running',
    camera: 'fa-video',
    light: 'fa-lightbulb',
    audio: 'fa-music',
    model: 'fa-user',
    mimik: 'fa-smile',
    script: 'fa-scroll',
    effekte: 'fa-gauge-high',
};

export const state = {
    renderer: null,
    scene: null,
    camera: null,
    controls: null,
    clock: new THREE.Clock(),

    project: new Timeline(),   // Timeline instance with typed track lists

    selectedTrackIdx: -1,
    selectedClipIdx: -1,
    playheadFrame: 0,
    playing: false,
    playbackSpeed: 1,
    endlos: false,        // „Endlos": am Ende der letzten Animation von vorn (Endlosschalter)
    timelineZoom: 100,  // pixels per second
    timelineScrollX: 0,

    // Camera edit mode state
    cameraEditMode: false,

    // Gruppe „Licht" startet zugeklappt (Edgar, 22.09.2026: „ständig
    // aufgeklappt beim Laden") — „Szene" bleibt offen, wie bisher.
    lightGroupCollapsed: true,

    // Undo suppression
    _undoSuppressed: false,
    _undoInProgress: false,
};

export const SESSION_KEY = 'bvhStudio_sessionState';
