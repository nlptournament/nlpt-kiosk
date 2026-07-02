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
    loop = input.required<boolean>();
    repeat = input.required<number>();
    finished = output<null>();

    media_id: string = '';
    playCount: number = 0;

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
                    this.playCount = 0;
                    myVideo.src = this.mediaService.getMediaUrl(media);
                    if (this.loop()) myVideo.loop = true;
                    else myVideo.loop = false;
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

    onVideoEnded() {
        if (this.playCount < this.repeat()) {
            this.playCount++;
            var myVideo: any = document.getElementById("player");
            myVideo.currentTime = 0;
            myVideo.play();
        } else {
            this.finished.emit(null);
        }
    }
}
