import { Component, input, model } from '@angular/core';

import { Media } from '../../../interfaces/media';
import { User } from '../../../interfaces/user';

import { MediaComponent } from '../../elements/media/media.component';
import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';

@Component({
  selector: 'panel-media',
  imports: [CommonModule, MediaComponent, Dialog],
  templateUrl: './media-panel.component.html',
  styleUrl: './media-panel.component.scss'
})
export class MediaPanelComponent {
    medias =  input.required<Map<string, Media>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    createMediaActive: boolean = false;
    createMediaDummy: Media = <Media>{};

    createMedia() {
        this.createMediaDummy = <Media>{user_id: this.currentUser().id, common: true, src_type: 1, type: 0, src: '', desc: ''};
        this.createMediaActive = true;
    }

    createdMedia(event: string|null|undefined) {
        this.createMediaActive = false;
    }

    closeDialog() {
        this.isActive.set(false);
    }
}
