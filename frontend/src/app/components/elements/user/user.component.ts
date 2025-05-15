import { booleanAttribute, Component, input, OnInit, output } from '@angular/core';
import { User } from '../../../interfaces/user';
import { UserService } from '../../../services/user.service';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { Checkbox } from 'primeng/checkbox';
import { TooltipModule } from 'primeng/tooltip';
import { Dialog } from 'primeng/dialog';
import { PasswordModule } from 'primeng/password';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'element-user',
  imports: [CommonModule, FormsModule, InputTextModule, Checkbox, TooltipModule, Dialog, PasswordModule, FloatLabelModule, ButtonModule],
  templateUrl: './user.component.html',
  styleUrl: './user.component.scss'
})
export class UserComponent implements OnInit {
    user = input.required<User>();
    currentUser = input.required<User>();
    editMode = input(false, {transform: booleanAttribute});
    editResult = output<string|null|undefined>();

    editActive: boolean = false;
    pwChangeActive: boolean = false;

    old_pw: string = "";
    new_pw: string = "";
    error_msg: string = "";

    constructor(
        private userService: UserService
    ) { }

    ngOnInit(): void {
        this.editActive = this.editMode();
    }

    editClose() {
        this.editResult.emit(this.user().id);
        this.editActive = false;
    }

    saveUser() {
        if (this.user().id) {
            this.userService
                .updateUser(this.user())
                .subscribe((result: any) => {
                    next: this.editClose();
                });
        }
        else {
            this.userService
                .createUser(this.user())
                .subscribe((result: any) => {
                    next: this.editClose();
                });
        }
    }

    deleteUser() {
        if (this.user().id) {
            this.userService
                .deleteUser(this.user().id!)
                .subscribe((result: any) => {
                    next: this.editClose();
                });
        }
    }

    submitPassword() {
        this.error_msg = "";
        if (this.new_pw == "") {
            this.error_msg = "New Password can't be empty";
            return;
        }
        if (this.old_pw == "") {
            this.error_msg = "Your Password can't be empty";
            return;
        }
        if (this.user().id) {
            this.userService
                .updatePw(this.user().id!, this.old_pw, this.new_pw)
                .subscribe({
                    next: () => {
                        this.pwChangeActive = false;
                    },
                    error: () => {
                        this.error_msg = "Your Password invalid";
                    }
                });
        }
    }
}
