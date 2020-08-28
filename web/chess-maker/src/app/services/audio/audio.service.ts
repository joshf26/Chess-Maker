import {Injectable} from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class AudioService {
    private plyAudio: HTMLAudioElement;

    constructor() {
        this.plyAudio = new Audio('assets/audio/ply.ogg');
    }

    playPly(): void {
        this.plyAudio.currentTime = 0;
        this.plyAudio.play();
    }
}
