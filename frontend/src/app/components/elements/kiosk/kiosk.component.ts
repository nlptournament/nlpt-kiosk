import { Component, input, OnInit, output } from '@angular/core';
import { User } from '../../../interfaces/user';
import { Kiosk } from '../../../interfaces/kiosk';
import { TimelineTemplate } from '../../../interfaces/timeline-template';
import { CommonModule } from '@angular/common';
import { KioskService } from '../../../services/kiosk.service';
import { Dialog } from 'primeng/dialog';
import { IftaLabelModule } from 'primeng/iftalabel';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ButtonModule } from 'primeng/button';

interface selectableCommon {
    code: boolean,
    name: string
}

interface selectableUser {
    code: string;
    name: string;
}

@Component({
  selector: 'element-kiosk',
  imports: [CommonModule, Dialog, FormsModule, IftaLabelModule, InputTextModule, SelectModule, SelectButtonModule, ButtonModule],
  templateUrl: './kiosk.component.html',
  styleUrl: './kiosk.component.scss'
})
export class KioskComponent implements OnInit {
    kiosk = input.required<Kiosk>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    timelineTemplates = input.required<Map<string, TimelineTemplate>>();
    editResult = output<string|null|undefined>();

    editActive: boolean = false;
    selectableCommons: selectableCommon[] = [];
    selectableUsers: selectableUser[] = [];

    constructor (
        private kioskService: KioskService
    ) { }

    ngOnInit(): void {
        this.selectableCommons.push(<selectableCommon>{code: true, 'name': 'available2everyone'});
        this.selectableCommons.push(<selectableCommon>{code: false, 'name': 'just4owner'});
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login})
        }
        this.selectableUsers = su;
    }

    kioskAccept() {
        this.kiosk().added_by_id = this.currentUser().id;
        this.kioskSave();
    }

    kioskDelete() {
        this.kioskService
            .deleteKiosk(this.kiosk().id)
            .subscribe((result: any) => {
                next: this.editResult.emit(this.kiosk().id);
            });
    }

    kioskSave() {
        this.kioskService
            .updateKiosk(this.kiosk())
            .subscribe((result: any) => {
                next: {
                    if (this.editActive) this.editClose();
                    else this.editResult.emit(this.kiosk().id);
                }
            });
    }

    editOpen() {
        this.createSelectableUsers();
        this.editActive = true;
    }

    editClose() {
        if (this.editActive) {
            this.editResult.emit(this.kiosk().id);
            this.editActive = false;
        }
    }
}
