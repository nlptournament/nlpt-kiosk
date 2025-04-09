import { CommonModule } from '@angular/common';
import { Component, input, OnInit } from '@angular/core';

@Component({
  selector: 'screen-logo-starfield',
  imports: [CommonModule],
  templateUrl: './logo-starfield.component.html',
  styleUrl: './logo-starfield.component.scss'
})
export class LogoStarfieldComponent implements OnInit {
    isActive = input.required<boolean>();
    variables = input.required<any>();

    title: string | undefined | null;
    subtitle: string | undefined | null;

    ngOnInit(): void {
        if (Object.keys(this.variables()).includes('text_above')) this.title = this.variables()['text_above'];
        if (Object.keys(this.variables()).includes('text_below')) this.subtitle = this.variables()['text_below'];
    }
}
