import { Component, input, model, OnInit } from '@angular/core';

import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Screen } from '../../../interfaces/screen';
import { Media } from '../../../interfaces/media';

import { CommonModule } from '@angular/common';
import { ScreenComponent } from '../../elements/screen/screen.component';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { TooltipModule } from 'primeng/tooltip';
import { InputTextModule } from 'primeng/inputtext';

interface selectableUser {
    code: string | null;
    name: string;
}

interface selectableTemplate {
    code: string | null;
    name: string;
}

@Component({
  selector: 'panel-screens',
  imports: [CommonModule, ScreenComponent, Dialog, TooltipModule, FormsModule, SelectModule, InputTextModule],
  templateUrl: './screens-panel.component.html',
  styleUrl: './screens-panel.component.scss'
})
export class ScreensPanelComponent implements OnInit {
    screens = input.required<Map<string, Screen>>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    medias = input.required<Map<string, Media>>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    selectableUsers: selectableUser[] = [];
    selectableTemplates: selectableTemplate[] = [];
    createScreenActive: boolean = false;
    createScreenDummy: Screen = <Screen>{};

    showHiddenScreens: boolean = false;
    showLockedScreens: boolean = false;
    ignoreScreenLocks: boolean = true;
    showAllDetails: boolean = false;  // if true all Screens are instructed to show teir details
    filterDesc: string = "";
    filterUser: string | null = null;
    filterTemplate: string | null = null;

    ngOnInit(): void {
        this.createSelectableUsers();
        this.createSelectableTemplates();
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        su.push(<selectableUser>{code: null, name: 'user'});
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login});
        }
        this.selectableUsers = su;
    }

    createSelectableTemplates() {
        let st: selectableTemplate[] = [];
        st.push(<selectableTemplate>{code: null, name: 'template'});
        for (let k of this.screenTemplates().keys()) {
            st.push(<selectableTemplate>{code: k, name: this.screenTemplates().get(k)!.name});
        }
        this.selectableTemplates = st;
    }

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
