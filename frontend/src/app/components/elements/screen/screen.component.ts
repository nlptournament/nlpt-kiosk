import { booleanAttribute, Component, input, OnInit } from '@angular/core';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { CommonModule } from '@angular/common';

interface variable_def {
    val: any;
    type: string;
    desc: string;
}

@Component({
  selector: 'element-screen',
  imports: [CommonModule],
  templateUrl: './screen.component.html',
  styleUrl: './screen.component.scss'
})
export class ScreenComponent implements OnInit {
    screen =  input.required<Screen>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    showDetails = input(false, {transform: booleanAttribute});
    overrideDetails: boolean = false;
    variables: Map<string, variable_def> = new Map<string, variable_def>;

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
}
