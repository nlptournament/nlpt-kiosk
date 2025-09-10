import { Component, input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'screen-text',
  imports: [CommonModule],
  templateUrl: './text.component.html',
  styleUrl: './text.component.scss'
})
export class TextComponent implements OnInit, OnChanges {
    isActive = input.required<boolean>();
    variables = input.required<any>();

    text: string[] = [];
    text_color: string | undefined;
    text_size: number = 9;

    constructor() {}

    ngOnInit(): void {
        this.extractVariables();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (Object.keys(changes).includes('variables')) this.extractVariables();
    }

    extractVariables() {
        if (Object.keys(this.variables()).includes('text') && this.variables()['text'] != '')
            this.text = this.variables()['text'].split('\n');
        else
            this.text = [];
        if (Object.keys(this.variables()).includes('text_color') && this.variables()['text_color'] != '')
            this.text_color = this.variables()['text_color'];
        else
            this.text_color = undefined;
        if (Object.keys(this.variables()).includes('text_size') && this.variables()['text_size'] > 0 && this.variables()['text_size'] < 15)
            this.text_size = this.variables()['text_size'];
        else
            this.text_size = 9;
    }
}
