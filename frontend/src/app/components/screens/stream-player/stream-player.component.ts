import { Component, ElementRef, input, OnChanges, OnDestroy, OnInit, SimpleChanges, ViewChild } from '@angular/core';

import { MediaService } from '../../../services/media.service';
import { Media } from '../../../interfaces/media';

import videojs from 'video.js';
import Player from 'video.js/dist/types/player';
import 'videojs-overlay';

@Component({
  selector: 'screen-stream-player',
  imports: [],
  templateUrl: './stream-player.component.html',
  styleUrl: './stream-player.component.scss'
})
export class StreamPlayerComponent implements OnInit, OnChanges, OnDestroy {
    @ViewChild('player', {static: true}) playerElement: ElementRef | undefined;
    player: Player | undefined;

    isActive = input.required<boolean>();
    header = input.required<string>();
    variables = input.required<any>();

    media_id: string = '';

    constructor(
        private mediaService: MediaService
    ) { }

    ngOnInit(): void {
        let player_conf = {
            'width': window.screen.width,
            'preload': 'auto',
            'plugins': {}
        }
        if (this.header() != '') {
            // converting position-definition to tailwind instructions (e.g.: top-left gets top-0 text-left)
            let header_pos: string = `${this.variables()['header_pos'].split('-')[0]}-0 text-${this.variables()['header_pos'].split('-')[1]}`;
            // converting size-definition to tailwind instruction (e.g.: 4 gets text-7xl)
            let header_size: string = `text-${Math.max(1, Math.min(7, this.variables()['header_size'])) + 3}xl`
            player_conf['plugins'] = {
                overlay: {
                    overlays: [{
                        start: 'play',
                        end: 'pause',
                        content: this.header(),
                        class: `font-orbitron ml-3 mr-3 mb-3 absolute z-10 ${header_size} ${header_pos} left-0 right-0 [text-shadow:_0_0_10px_rgba(0,0,0,0.8),0_2px_4px_rgba(0,0,0,0.6)]`
                    }]
                }
            }
        }
        this.player = videojs(this.playerElement!.nativeElement, player_conf);
        this.extractVariables();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (Object.keys(changes).includes('variables')) this.extractVariables();
        if (Object.keys(changes).includes('isActive')) this.startPlaying();
    }

    ngOnDestroy(): void {
        if (this.player) this.player.dispose();
    }

    extractVariables() {
        this.mediaService
            .getMedia(this.variables()['stream'])
            .subscribe({
                next: (media: Media) => {
                    this.media_id = media.id;
                    if (this.player) {
                        this.player.src({src: this.mediaService.getMediaUrl(media), type: "application/x-mpegURL"});
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
