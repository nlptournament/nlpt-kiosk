import { Component, input, model } from '@angular/core';

import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { Media } from '../../../interfaces/media';

import { CommonModule } from '@angular/common';
import { ScreenComponent } from '../../elements/screen/screen.component';
import { Dialog } from 'primeng/dialog';

@Component({
  selector: 'panel-screens',
  imports: [CommonModule, ScreenComponent, Dialog],
  templateUrl: './screens-panel.component.html',
  styleUrl: './screens-panel.component.scss'
})
export class ScreensPanelComponent {
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    medias = input.required<Map<string, Media>>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    createScreenActive: boolean = false;
    createScreenDummy: Screen = <Screen>{};

    createScreen() {
        this.createScreenDummy = <Screen>{desc: '', user_id: this.currentUser().id, duration: null, repeat: 0, loop: false, variables: {}};
        this.createScreenActive = true;
    }

    screenCreated(event: string|null|undefined) {
        this.createScreenActive = false;
    }

    closeDialog() {
        this.isActive.set(false);
    }

}
