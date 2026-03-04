import { Component, input, model } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';

import { User } from '../../../interfaces/user';

import { UserService } from '../../../services/user.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';

import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'panel-profile',
  imports: [CommonModule, Dialog, FormsModule, ToggleSwitchModule, ButtonModule],
  templateUrl: './profile-panel.component.html',
  styleUrl: './profile-panel.component.scss'
})
export class ProfilePanelComponent {
    currentUser = input.required<User>();
    isActive = model.required<boolean>();

    isVisible: boolean = true;

    constructor(
        private userService: UserService,
        private errorHandler: ErrorHandlerService
    ) {}

    saveProfile() {
        this.userService.updateUser(this.currentUser()).subscribe({
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
