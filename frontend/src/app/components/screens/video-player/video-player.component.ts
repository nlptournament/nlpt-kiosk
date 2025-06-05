import { Component, ElementRef, input, output, SimpleChanges, ViewChild } from '@angular/core';

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
    @ViewChild('video') videoElement: ElementRef | undefined;

    isActive = input.required<boolean>();
    variables = input.required<any>();
    finished = output<null>();

    video_id: string = '';

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
                    var myVideo: any = document.getElementById("video");
                    this.video_id = media.id;
                    myVideo.src = this.mediaService.getMediaUrl(media);
                    myVideo.currentTime = 0;
                    this.startPlaying();
                },
                error: () => {
                    this.video_id = '';
                }
            });
    }

    startPlaying() {
        if (this.isActive() && this.video_id != '') {
            var myVideo: any = document.getElementById("video");
            if (myVideo.paused) myVideo.play();
        }
    }
}
