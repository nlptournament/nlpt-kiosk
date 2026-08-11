import { Routes } from '@angular/router';

import { DisplayComponent } from './components/display/display.component';
import { LoginComponent } from './components/admin/login/login.component';
import { AdminScreenComponent } from './components/admin/admin-screen/admin-screen.component';
import { StreamerScreenComponent } from './components/streamer/streamer-screen/streamer-screen.component';
import { LogoutComponent } from './components/admin/logout/logout.component';
import { PresenterScreenComponent } from './components/presenter/presenter-screen/presenter-screen.component';

export const routes: Routes = [
    { path: 'display', component: DisplayComponent },
    { path: 'login', component: LoginComponent },
    { path: 'logout', component: LogoutComponent },
    { path: 'admin', component: AdminScreenComponent },
    { path: 'streamer', component: StreamerScreenComponent },
    { path: 'present', component: PresenterScreenComponent},
    { path: '**', component: DisplayComponent }
];
