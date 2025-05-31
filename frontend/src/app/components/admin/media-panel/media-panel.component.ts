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

    createMedia() {}

    closeDialog() {
        this.isActive.set(false);
    }
}
