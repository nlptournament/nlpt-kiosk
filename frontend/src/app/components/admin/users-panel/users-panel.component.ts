import { Component, input, model } from '@angular/core';
import { User } from '../../../interfaces/user';

import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { UserComponent } from '../../elements/user/user.component';

@Component({
  selector: 'panel-users',
  imports: [CommonModule, Dialog, UserComponent],
  templateUrl: './users-panel.component.html',
  styleUrl: './users-panel.component.scss'
})
export class UsersPanelComponent {
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    isActive = model.required<boolean>();
}
