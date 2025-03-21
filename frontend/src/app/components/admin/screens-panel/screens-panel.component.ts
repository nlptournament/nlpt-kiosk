import { Component, input, model, output } from '@angular/core';

import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';

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
    screenEdited = output<string|null|undefined>();
    isActive = model.required<boolean>();

    createScreenActive: boolean = false;
    createScreenDummy: Screen = <Screen>{};

    createScreen() {
        this.createScreenDummy = <Screen>{desc: '', user_id: this.currentUser().id, duration: null, repeat: 0, loop: false, variables: {}};
        this.createScreenActive = true;
    }

    screenCreated(event: string|null|undefined) {
        this.screenEdited.emit(event);
        this.createScreenActive = false;
    }

}
