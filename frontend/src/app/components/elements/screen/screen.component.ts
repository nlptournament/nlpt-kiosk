import { booleanAttribute, Component, input, OnInit, output } from '@angular/core';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { IftaLabelModule } from 'primeng/iftalabel';
import { ButtonModule } from 'primeng/button';
import { ScreenService } from '../../../services/screen.service';

interface variable_def {
    val: any;
    type: string;
    desc: string;
}

@Component({
  selector: 'element-screen',
  imports: [CommonModule, Dialog, FormsModule, InputTextModule, IftaLabelModule, ButtonModule],
  templateUrl: './screen.component.html',
  styleUrl: './screen.component.scss'
})
export class ScreenComponent implements OnInit {
    screen =  input.required<Screen>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    showDetails = input(false, {transform: booleanAttribute});
    editMode = input(false, {transform: booleanAttribute});
    editResult = output<string|null|undefined>();
    overrideDetails: boolean = false;
    editActive: boolean = false;
    variables: Map<string, variable_def> = new Map<string, variable_def>;

    constructor(
        private screenService: ScreenService
    ) { }

    ngOnInit(): void {
        this.extractVariables();
    }

    extractVariables() {
        if (this.screen().variables && this.screen().template_id && this.screenTemplates().has(this.screen().template_id!)) {
            let v: Map<string, variable_def> = new Map<string, variable_def>;
            let st: ScreenTemplate = this.screenTemplates().get(this.screen().template_id!)!;
            for (let key of Object.keys(st.variables_def)) {
                if (Object.keys(st.variables_def[key]).includes('ro') && st.variables_def[key]['ro'] == true) continue;  // skip ro variables
                let o: variable_def = <variable_def>{val: undefined, type: '', desc: ''};
                if (Object.keys(this.screen().variables).includes(key)) o.val = this.screen().variables[key];
                else if (Object.keys(st.variables_def[key]).includes('default')) o.val = st.variables_def[key]['default']
                if (Object.keys(st.variables_def[key]).includes('desc')) o.desc = st.variables_def[key]['desc']
                o.type = st.variables_def[key]['type']
                v.set(key, o);
            }
            Object.keys
            this.variables = v;
        }
    }

    toggleOverrideDetails() {
        this.overrideDetails = !this.overrideDetails;
    }

    editClose() {
        if (this.editMode())
            this.editResult.emit(this.screen().id);
    }

    editClosed(event: string|null|undefined) {
        if (event) this.editResult.emit(event);
        this.editActive = false;
    }

    saveScreen() {
        if (this.editMode())
            this.screenService
                .updateScreen(this.screen())
                .subscribe((result: any) => {
                    next: this.editClose();
                });
    }
}
