import { booleanAttribute, Component, input, OnChanges, OnInit, output, SimpleChanges } from '@angular/core';
import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { CommonModule } from '@angular/common';
import { Dialog } from 'primeng/dialog';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { IftaLabelModule } from 'primeng/iftalabel';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';
import { TooltipModule } from 'primeng/tooltip';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectButtonModule } from 'primeng/selectbutton';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { DatePickerModule } from 'primeng/datepicker';
import { ScreenService } from '../../../services/screen.service';

interface variableDef {
    val: any;
    type: string;
    desc: string;
}

interface selectableTemplate {
    code: string;
    name: string;
    desc: string;
}

interface selectableLoop {
    code: boolean,
    name: string
}

interface selectableUser {
    code: string;
    name: string;
}

@Component({
  selector: 'element-screen',
  imports: [CommonModule, Dialog, FormsModule, InputTextModule, IftaLabelModule, ButtonModule, SelectModule, TooltipModule, InputNumberModule, SelectButtonModule, ToggleSwitchModule, DatePickerModule],
  templateUrl: './screen.component.html',
  styleUrl: './screen.component.scss'
})
export class ScreenComponent implements OnInit, OnChanges {
    screen =  input.required<Screen>();
    screenTemplates = input.required<Map<string, ScreenTemplate>>();
    users = input.required<Map<string, User>>();
    currentUser = input.required<User>();
    showDetails = input(false, {transform: booleanAttribute});
    editMode = input(false, {transform: booleanAttribute});
    roMode = input(false, {transform: booleanAttribute});
    editResult = output<string|null|undefined>();

    overrideDetails: boolean = false;
    editActive: boolean = false;
    variables: Map<string, variableDef> = new Map<string, variableDef>;
    selectableTemplates: selectableTemplate[] = [];
    selectableLoops: selectableLoop[] = [];
    selectableUsers: selectableUser[] = [];

    constructor(
        private screenService: ScreenService
    ) { }

    ngOnInit(): void {
        this.extractVariables();
        if (this.editMode()) {
            this.createSelectableTemplates();
            this.createSelectableUsers();
            this.selectableLoops.push(<selectableLoop>{code: true, 'name': 'endless'});
            this.selectableLoops.push(<selectableLoop>{code: false, 'name': 'just repeat'});
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (!this.editMode() && Object.keys(changes).includes('screen')) {
            this.extractVariables();
        }
    }

    extractVariables() {
        if (this.screen().variables && this.screen().template_id && this.screenTemplates().has(this.screen().template_id!)) {
            let v: Map<string, variableDef> = new Map<string, variableDef>;
            let st: ScreenTemplate = this.screenTemplates().get(this.screen().template_id!)!;
            for (let key of Object.keys(st.variables_def)) {
                if (Object.keys(st.variables_def[key]).includes('ro') && st.variables_def[key]['ro'] == true) continue;  // skip ro variables
                let o: variableDef = <variableDef>{val: undefined, type: '', desc: ''};
                if (Object.keys(this.screen().variables).includes(key)) o.val = this.screen().variables[key];
                else if (Object.keys(st.variables_def[key]).includes('default')) o.val = st.variables_def[key]['default']
                if (Object.keys(st.variables_def[key]).includes('desc')) o.desc = st.variables_def[key]['desc']
                o.type = st.variables_def[key]['type']
                if (o.type == 'ts') {
                    if (o.val && Number(o.val)) o.val = new Date(Number(o.val) * 1000);
                    else o.val = new Date(Date.now());
                }
                v.set(key, o);
            }
            Object.keys
            this.variables = v;
        }
    }

    writeVariables() {
        let nv = {};
        for (let k of this.variables.keys()) {
            if (this.variables.get(k)!.type == 'ts') {
                let date: Date = this.variables.get(k)!.val;
                nv = { ...nv, [k]: Math.floor(date.getTime() / 1000)};
            }
            else nv = { ...nv, [k]: this.variables.get(k)!.val};
        }
        this.screen().variables = nv;
    }

    createSelectableTemplates() {
        let st: selectableTemplate[] = [];
        for (let k of this.screenTemplates().keys()) {
            st.push(<selectableTemplate>{code: k, name: this.screenTemplates().get(k)!.name, desc: this.screenTemplates().get(k)!.desc})
        }
        this.selectableTemplates = st;
    }

    createSelectableUsers() {
        let su: selectableUser[] = [];
        for (let k of this.users().keys()) {
            su.push(<selectableUser>{code: k, name: this.users().get(k)!.login})
        }
        this.selectableUsers = su;
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

    templateChanged() {
        this.extractVariables();
    }

    saveScreen() {
        if (this.editMode()) {
            this.writeVariables();
            if (this.screen().id)
                this.screenService
                    .updateScreen(this.screen())
                    .subscribe((result: any) => {
                        next: this.editClose();
                    });
            else
                this.screenService
                    .createScreen(this.screen())
                    .subscribe((result: any) => {
                        next: {
                            if (Object.keys(result).includes('created'))
                                this.screen().id = result['created'];
                            this.editClose();
                        }
                    });
        }
    }

    duplicateScreen() {
        let cs: Screen = this.screen();
        let s: Screen = <Screen>{desc: cs.desc + ' - duplacate', template_id: cs.template_id, user_id: this.currentUser().id, duration: cs.duration, repeat: cs.repeat, loop: cs.loop, variables: cs.variables};
        this.screenService
            .createScreen(s)
            .subscribe((result: any) => {
                next: {
                    if (Object.keys(result).includes('created')) this.editResult.emit(result['created']);
                }
            });
    }

    deleteScreen() {
        if (this.editMode() && this.screen().id)
            this.screenService
                .deleteScreen(this.screen().id!)
                .subscribe((result: any) => {
                    next: this.editClose();
                });
        else this.editClose();
    }
}
