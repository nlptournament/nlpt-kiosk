import { Component, input, output, SimpleChanges } from '@angular/core';

import { CommonModule } from '@angular/common';
import { MediaService } from '../../../services/media.service';
import { Media } from '../../../interfaces/media';

@Component({
  selector: 'screen-video-player',
  imports: [CommonModule],
  templateUrl: './video-player.component.html',
  styleUrl: './video-player.component.scss'
})
export class VideoPlayerComponent {
    isActive = input.required<boolean>();
    header = input.required<string>();
    variables = input.required<any>();
    finished = output<null>();

    media_id: string = '';

    constructor(
        private mediaService: MediaService
    ) { }

    ngOnInit(): void {
        this.extractVariables();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (Object.keys(changes).includes('variables')) this.extractVariables();
        if (Object.keys(changes).includes('isActive')) this.startPlaying();
    }

    extractVariables() {
        this.mediaService
            .getMedia(this.variables()['video'])
            .subscribe({
                next: (media: Media) => {
                    var myVideo: any = document.getElementById("player");
                    this.media_id = media.id;
                    myVideo.src = this.mediaService.getMediaUrl(media);
                    myVideo.currentTime = 0;
                    this.startPlaying();
                },
                error: () => {
                    this.media_id = '';
                }
            });
    }

    startPlaying() {
        if (this.isActive() && this.media_id != '') {
            var myVideo: any = document.getElementById("player");
            if (myVideo.paused) myVideo.play();
        }
    }
}
