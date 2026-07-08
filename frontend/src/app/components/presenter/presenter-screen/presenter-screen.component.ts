import { Component, OnInit } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { MenuItem } from 'primeng/api';
import { MenubarModule } from 'primeng/menubar';
import { TooltipModule } from 'primeng/tooltip';

import { User } from '../../../interfaces/user';

import { ErrorHandlerService } from '../../../services/error-handler.service';
import { PresentationService } from '../../../services/presentation.service';
import { UserService } from '../../../services/user.service';

import { ProfilePanelComponent } from '../../admin/profile-panel/profile-panel.component';
import { UpdatePwComponent } from '../../admin/update-pw/update-pw.component';

@Component({
  selector: 'app-presenter-screen',
  imports: [CommonModule, MenubarModule, TooltipModule, ProfilePanelComponent, UpdatePwComponent],
  templateUrl: './presenter-screen.component.html',
  styleUrl: './presenter-screen.component.scss'
})
export class PresenterScreenComponent implements OnInit {
    menuItems: MenuItem[] = [];
    currentUser!: User;
    showHiddenKiosks: boolean = false;
    updatePwActive: boolean = false;
    panelProfileActive: boolean = false;

    constructor(
        private errorHandler: ErrorHandlerService,
        private router: Router,
        private presentationService: PresentationService,
        private userService: UserService
    ) { }

    ngOnInit(): void {
        this.populateMenu();
        this.refreshUsers();
    }

    populateMenu() {
        this.menuItems = [
            {
                label: 'User',
                icon: 'pi pi-user',
                items: [
                    {
                        label: this.currentUser?.login,
                        disabled: true
                    },
                    {
                        label: 'Change Password',
                        icon: 'pi pi-key',
                        command: () => {
                            this.updatePwActive = true;
                        }
                    },
                    {
                        label: 'Profile',
                        icon: 'pi pi-cog',
                        command: () => {
                            this.panelProfileActive = true;
                        }
                    },
                    {
                        label: 'Show hidden Kiosks',
                        icon: 'pi pi-eye',
                        visible: !this.showHiddenKiosks,
                        command: () => {
                            this.showHiddenKiosks = true;
                            this.populateMenu();
                        }
                    },
                    {
                        label: 'Suppress hidden Kiosks',
                        icon: 'pi pi-eye-slash',
                        visible: this.showHiddenKiosks,
                        command: () => {
                            this.showHiddenKiosks = false;
                            this.populateMenu();
                        }
                    },
                    {
                        separator: true
                    },
                    {
                        label: 'Admin Interface',
                        icon: 'pi pi-hammer',
                        command: () => {
                            this.router.navigate(['/admin']);
                        }
                    },
                    {
                        separator: true
                    },
                    {
                        label: 'Logout',
                        icon: 'pi pi-sign-out',
                        command: () => {
                            this.router.navigate(['/logout']);
                        }
                    },
                ]
            },
        ]
    }

    execForward() {
        this.presentationService.execForward().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    execBackward() {
        this.presentationService.execBackward().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    execRestart() {
        this.presentationService.execRestart().subscribe({
            next: (result: any) => {},
            error: (err: HttpErrorResponse) => {
                this.errorHandler.handleError(err);
            }
        });
    }

    refreshUsers(): void {
        this.userService.getMe().subscribe({
            next: (user: User) => {
                this.currentUser = user;
            },
            error: (error: HttpErrorResponse) => {
                this.errorHandler.handleError(error);
            }
        });
    }
}
