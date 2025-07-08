import { Component, input, model, OnInit } from '@angular/core';

import { Media, MediaType, MediaSrcType } from '../../../interfaces/media';
import { User } from '../../../interfaces/user';

import { MediaComponent } from '../../elements/media/media.component';
import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { InputTextModule } from 'primeng/inputtext';

interface selectableType {
    code: number | null;
    name: string;
}

interface selectableUser {
    code: string | null;
    name: string;
}

@Component({
  selector: 'panel-media',
  imports: [CommonModule, MediaComponent, Dialog, FormsModule, SelectModule, InputTextModule],
  templateUrl: './media-panel.component.html',
  styleUrl: './media-panel.component.scss'
})
export class MediaPanelComponent implements OnInit {
    medias =  input.required<Map<string, Media>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    createMediaActive: boolean = false;
    createMediaDummy: Media = <Media>{};
    selectableSrcTypes: selectableType[] = [];
    selectableTypes: selectableType[] = [];
    selectableUsers: selectableUser[] = [];

    showHiddenMedia: boolean = false;
    filterDesc: string = "";
    filterType: number | null = null;
    filterSrcType: number | null = null;
    filterUser: string | null = null;
    filterCommon: boolean | null = null;

    ngOnInit(): void {
        this.createSelectableTypes();
        this.createSelectableUsers();
    }

    createSelectableTypes() {
        let st: selectableType[] = [];
        st.push(<selectableType>{code: null, name: 'type'});
        let vt = Object.values(MediaType);
        for (let i = 0; i < vt.length / 2; i++) {
            st.push(<selectableType>{code: i, name: vt[i]});
        }
        this.selectableTypes = st;
        st = [];
        st.push(<selectableType>{code: null, name: 'src type'});
        let vst = Object.values(MediaSrcType);
        for (let i = 0; i < vst.length / 2; i++) {
            st.push(<selectableType>{code: i, name: vst[i]});
        }
        this.selectableSrcTypes = st;
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        su.push(<selectableUser>{code: null, name: 'user'})
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login})
        }
        this.selectableUsers = su;
    }

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
