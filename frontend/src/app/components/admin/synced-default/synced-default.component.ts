import { Component, input, model, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';

import { KioskService } from '../../../services/kiosk.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';

import { Kiosk } from '../../../interfaces/kiosk';
import { User } from '../../../interfaces/user';

import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { ButtonModule } from 'primeng/button';

interface selectabelKiosk {
    name: string;
    id: string;
    selected: boolean;
    enabled: boolean;
}

@Component({
  selector: 'synced-apply-default',
  imports: [CommonModule, Dialog, FormsModule, ToggleSwitchModule, ButtonModule],
  templateUrl: './synced-default.component.html',
  styleUrl: './synced-default.component.scss'
})
export class SyncedDefaultComponent implements OnInit {
    kiosks = input.required<Map<string, Kiosk>>();
    currentUser = input.required<User>();
    showHiddenKiosks = input.required<boolean>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;
    selectableKiosks: selectabelKiosk[] = [];

    constructor(
        private kioskService: KioskService,
        private errorHandler: ErrorHandlerService
    ) {}

    ngOnInit(): void {
        this.createSelectableKiosks();
    }

    createSelectableKiosks() {
        let sks: selectabelKiosk[] = [];
        for (let kiosk of this.kiosks().values()) {
            if (!this.currentUser().admin && !kiosk.common && kiosk.added_by_id != this.currentUser().id) continue;
            let sk: selectabelKiosk = <selectabelKiosk>{id: kiosk.id, name: kiosk.name};
            if (kiosk.desc != "") sk.name = kiosk.desc;

            if (this.currentUser().hidden_elements.includes(kiosk.id) && kiosk.default_timeline_id) {
                sk.enabled = true;
                if (this.showHiddenKiosks()) sk.selected = true;
                else sk.selected = false;
            }
            else if (kiosk.default_timeline_id) {
                sk.enabled = true;
                sk.selected = true;
            }
            else {
                sk.enabled = false;
                sk.selected = false;
            }
            sks.push(sk);
        }
        this.selectableKiosks = sks;
    }

    applyDefaults() {
        let kiosk_ids: string[] = [];
        for (let kiosk of this.selectableKiosks) {
            if (kiosk.selected) kiosk_ids.push(kiosk.id);
        }
        this.kioskService.syncedApplyDefault(kiosk_ids).subscribe({
            next: () => {
                this.closeDialog();
            },
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    closeDialog() {
        this.isActive.set(false);
    }
}
