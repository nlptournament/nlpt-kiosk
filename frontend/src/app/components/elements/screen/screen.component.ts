import { Component, input } from '@angular/core';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';

@Component({
  selector: 'element-screen',
  imports: [],
  templateUrl: './screen.component.html',
  styleUrl: './screen.component.scss'
})
export class ScreenComponent {
    screen =  input.required<Screen>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
}
