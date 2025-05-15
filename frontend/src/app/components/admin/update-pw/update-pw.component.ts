import { Component, input, model } from '@angular/core';
import { CommonModule } from '@angular/common';

import { User } from '../../../interfaces/user';
import { UserService } from '../../../services/user.service';

import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { PasswordModule } from 'primeng/password';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'update-pw',
  imports: [CommonModule, Dialog, FormsModule, PasswordModule, FloatLabelModule, ButtonModule],
  templateUrl: './update-pw.component.html',
  styleUrl: './update-pw.component.scss'
})
export class UpdatePwComponent {
    currentUser = input.required<User>();
    isActive = model.required<boolean>();

    old_pw: string = "";
    new_pw_1: string = "";
    new_pw_2: string = "";
    error_msg: string = "";

    constructor (
        private userService: UserService
    ) {}

    submitChange() {
        this.error_msg = "";
        if (this.new_pw_1 != this.new_pw_2) {
            this.error_msg = "New Passwords don't match";
            return;
        }
        if (this.new_pw_1 == "") {
            this.error_msg = "New Password can't be empty";
            return;
        }
        if (this.old_pw == "") {
            this.error_msg = "Old Password can't be empty";
            return;
        }
        if (this.currentUser().id) {
            this.userService
                .updatePw(this.currentUser().id!, this.old_pw, this.new_pw_1)
                .subscribe({
                    next: () => {
                        this.isActive.set(false);
                    },
                    error: () => {
                        this.error_msg = "Old Password invalid";
                    }
                });
        }
    }
}
