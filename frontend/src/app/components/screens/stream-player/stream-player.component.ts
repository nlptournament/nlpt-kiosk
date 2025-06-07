import { Component, ElementRef, input, SimpleChanges, ViewChild } from '@angular/core';

import { MediaService } from '../../../services/media.service';
import { Media } from '../../../interfaces/media';

import videojs from 'video.js';
import Player from 'video.js/dist/types/player';

@Component({
  selector: 'screen-stream-player',
  imports: [],
  templateUrl: './stream-player.component.html',
  styleUrl: './stream-player.component.scss'
})
export class StreamPlayerComponent {
    @ViewChild('player', {static: true}) playerElement: ElementRef | undefined;
    player: Player | undefined;

    isActive = input.required<boolean>();
    variables = input.required<any>();

    media_id: string = '';

    constructor(
        private mediaService: MediaService
    ) { }

    ngOnInit(): void {
        this.player = videojs(this.playerElement!.nativeElement, {'width': window.screen.width, 'preload': 'auto'});
        this.extractVariables();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (Object.keys(changes).includes('variables')) this.extractVariables();
        if (Object.keys(changes).includes('isActive')) this.startPlaying();
    }

    extractVariables() {
        this.mediaService
            .getMedia(this.variables()['stream'])
            .subscribe({
                next: (media: Media) => {
                    this.media_id = media.id;
                    if (this.player) {
                        this.player.src({src: this.mediaService.getMediaUrl(media), type: "application/x-mpegURL"});
                        this.player.currentTime(0);
                        this.startPlaying();
                    }
                },
                error: () => {
                    this.media_id = '';
                }
            });
    }

    startPlaying() {
        if (this.isActive() && this.media_id != '' && this.player) {
            if (this.player.paused()) {
                this.player.play();
            }
        }
    }

}
