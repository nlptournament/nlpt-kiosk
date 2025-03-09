import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MenuItem } from 'primeng/api';
import { SpeedDial } from 'primeng/speeddial';
import { UserService } from '../../../services/user.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';
import { User } from '../../../interfaces/user';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-admin-screen',
  imports: [SpeedDial],
  templateUrl: './admin-screen.component.html',
  styleUrl: './admin-screen.component.scss'
})
export class AdminScreenComponent implements OnInit {
    menuItems: MenuItem[] = [];
    currentUser!: User;

    constructor(
        private errorHandler: ErrorHandlerService,
        private router: Router,
        private userService: UserService
    ) { }

    ngOnInit(): void {
        this.populateMenu();
        this.refreshCurrentUser();
    }

    populateMenu() {
        this.menuItems = [
            {
                label: 'Logout',
                icon: 'pi pi-sign-out',
                command: () => {
                    this.router.navigate(['/logout']);
                }
            }
        ]
    }

    refreshCurrentUser() {
        this.userService
            .getMe()
            .subscribe({
                next: (user: User) => {
                    this.currentUser = user;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

}
