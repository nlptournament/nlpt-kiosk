import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MenuItem } from 'primeng/api';
import { SpeedDial } from 'primeng/speeddial';
import { UserService } from '../../../services/user.service';
import { ErrorHandlerService } from '../../../services/error-handler.service';
import { User } from '../../../interfaces/user';
import { HttpErrorResponse } from '@angular/common/http';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplateService } from '../../../services/screen-template.service';
import { ScreenService } from '../../../services/screen.service';
import { ScreenComponent } from '../../elements/screen/screen.component';

@Component({
  selector: 'app-admin-screen',
  imports: [SpeedDial, ScreenComponent],
  templateUrl: './admin-screen.component.html',
  styleUrl: './admin-screen.component.scss'
})
export class AdminScreenComponent implements OnInit {
    menuItems: MenuItem[] = [];
    currentUser!: User;
    users: Map<string, User> = new Map<string, User>;
    screenTemplates: Map<string, ScreenTemplate> = new Map<string, ScreenTemplate>;
    screens: Map<string, Screen> = new Map<string, Screen>;
    testscreen: Screen = <Screen>{desc: 'Hallo'};

    constructor(
        private errorHandler: ErrorHandlerService,
        private router: Router,
        private userService: UserService,
        private screenTemplateService: ScreenTemplateService,
        private screenService: ScreenService
    ) { }

    ngOnInit(): void {
        this.populateMenu();
        this.refreshUsers();
        this.refreshScreenTemplates();
        this.refreshScreens();
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

    refreshUsers() {
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
        this.userService
            .getUsers()
            .subscribe({
                next: (users: User[]) => {
                    let ul: Map<string, User> = new Map<string, User>;
                    for (let user of users) ul.set(user.id, user);
                    this.users = ul;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    refreshScreenTemplates() {
        this.screenTemplateService
            .getScreenTemplates()
            .subscribe({
                next: (sts: ScreenTemplate[]) => {
                    let stl: Map<string, ScreenTemplate> = new Map<string, ScreenTemplate>;
                    for (let st of sts) stl.set(st.id, st);
                    this.screenTemplates = stl;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

    refreshScreens() {
        this.screenService
            .getScreens()
            .subscribe({
                next: (screens: Screen[]) => {
                    let sl: Map<string, Screen> = new Map<string, Screen>;
                    for (let screen of screens) if (screen.id) sl.set(screen.id, screen);
                    this.screens = sl;
                },
                error: (err: HttpErrorResponse) => {
                    this.errorHandler.handleError(err);
                }
            });
    }

}
