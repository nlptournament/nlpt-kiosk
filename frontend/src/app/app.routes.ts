import { Routes } from '@angular/router';

import { DisplayComponent } from './components/display/display.component';
import { PlayerCountsComponent } from './components/screens/player-counts/player-counts.component';
import { TasComponent } from './components/screens/tas/tas.component';
import { TimerComponent } from './components/screens/timer/timer.component';
import { LogoStarfieldComponent } from './components/screens/logo-starfield/logo-starfield.component';
import { AnnouncementsComponent } from './components/screens/announcements/announcements.component';
import { LoginComponent } from './components/admin/login/login.component';
import { AdminScreenComponent } from './components/admin/admin-screen/admin-screen.component';
import { LogoutComponent } from './components/admin/logout/logout.component';

export const routes: Routes = [
    { path: 'display', component: DisplayComponent },
    { path: 'login', component: LoginComponent },
    { path: 'logout', component: LogoutComponent },
    { path: 'admin', component: AdminScreenComponent },
    { path: 'players', component: PlayerCountsComponent },
    { path: 'tas', component: TasComponent },
    { path: 'timer', component: TimerComponent },
    { path: 'starfield', component: LogoStarfieldComponent },
    { path: 'anno', component: AnnouncementsComponent },
    { path: '**', component: DisplayComponent }
];
