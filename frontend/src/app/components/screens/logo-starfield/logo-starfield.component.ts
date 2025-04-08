import { CommonModule } from '@angular/common';
import { Component, input } from '@angular/core';

@Component({
  selector: 'screen-logo-starfield',
  imports: [CommonModule],
  templateUrl: './logo-starfield.component.html',
  styleUrl: './logo-starfield.component.scss'
})
export class LogoStarfieldComponent {
    isActive = input.required<boolean>();

    title: string | undefined | null;
    subtitle: string | undefined | null;
}
