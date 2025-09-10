import { Routes } from '@angular/router';

import { DisplayComponent } from './components/display/display.component';
import { LoginComponent } from './components/admin/login/login.component';
import { AdminScreenComponent } from './components/admin/admin-screen/admin-screen.component';
import { LogoutComponent } from './components/admin/logout/logout.component';

export const routes: Routes = [
    { path: 'display', component: DisplayComponent },
    { path: 'login', component: LoginComponent },
    { path: 'logout', component: LogoutComponent },
    { path: 'admin', component: AdminScreenComponent },
    { path: '**', component: DisplayComponent }
];
