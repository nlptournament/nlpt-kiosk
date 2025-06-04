import { Component, input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MediaService } from '../../../services/media.service';
import { Media } from '../../../interfaces/media';

@Component({
  selector: 'screen-background-image',
  imports: [CommonModule],
  templateUrl: './background-image.component.html',
  styleUrl: './background-image.component.scss'
})
export class BackgroundImageComponent implements OnInit, OnChanges {
    isActive = input.required<boolean>();
    variables = input.required<any>();

    text_upper: string | undefined | null;
    text_lower: string | undefined | null;
    text_color: string | undefined;
    text_spaceing: number[] | undefined;
    image_id: string = '';
    image_url: string = '';

    constructor(
        private mediaService: MediaService
    ) { }

    ngOnInit(): void {
        this.extractVariables();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (Object.keys(changes).includes('variables')) this.extractVariables();
    }

    extractVariables() {
        if (Object.keys(this.variables()).includes('image') && this.variables()['image'] != this.image_id) {
            this.mediaService
                .getMedia(this.variables()['image'])
                .subscribe({
                    next: (media: Media) => {
                        this.image_id = media.id;
                        this.image_url = this.mediaService.getMediaUrl(media);
                    }
                });
        }
        if (Object.keys(this.variables()).includes('text_above') && this.variables()['text_above'] != '')
            this.text_upper = this.variables()['text_above'];
        else
            this.text_upper = null;
        if (Object.keys(this.variables()).includes('text_below') && this.variables()['text_below'] != '')
            this.text_lower = this.variables()['text_below'];
        else
            this.text_lower = null;
        if (Object.keys(this.variables()).includes('text_color') && this.variables()['text_color'] != '')
            this.text_color = this.variables()['text_color'];
        else
            this.text_color = undefined;
        if (Object.keys(this.variables()).includes('text_space') && this.variables()['text_space'] > 0)
            this.text_spaceing = Array(this.variables()['text_space']).fill(0).map((x,i)=>i);
        else
            this.text_spaceing = undefined;
    }
}
