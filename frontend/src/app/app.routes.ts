import { Routes } from '@angular/router';

import { DisplayScreenComponent } from './components/display-screen/display-screen.component';
import { PlayerCountsComponent } from './components/player-counts/player-counts.component';
import { TasComponent } from './components/tas/tas.component';
import { TimerComponent } from './components/timer/timer.component';
import { LogoStarfieldComponent } from './components/logo-starfield/logo-starfield.component';
import { AnnouncementsComponent } from './components/announcements/announcements.component';
import { LoginComponent } from './components/admin/login/login.component';
import { AdminScreenComponent } from './components/admin/admin-screen/admin-screen.component';

export const routes: Routes = [
    { path: 'display', component: DisplayScreenComponent },
    { path: 'login', component: LoginComponent },
    { path: 'admin', component: AdminScreenComponent },
    { path: 'players', component: PlayerCountsComponent },
    { path: 'tas', component: TasComponent },
    { path: 'timer', component: TimerComponent },
    { path: 'starfield', component: LogoStarfieldComponent },
    { path: 'anno', component: AnnouncementsComponent },
    { path: '**', component: DisplayScreenComponent }
];
