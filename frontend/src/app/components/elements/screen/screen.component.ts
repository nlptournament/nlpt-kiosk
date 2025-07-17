import { booleanAttribute, Component, input, OnChanges, OnInit, output, SimpleChanges } from '@angular/core';

import { ScreenService } from '../../../services/screen.service';

import { Screen } from '../../../interfaces/screen';
import { ScreenTemplate } from '../../../interfaces/screen-template';
import { User } from '../../../interfaces/user';
import { Media } from '../../../interfaces/media';

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
import { UserService } from '../../../services/user.service';

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

interface selectableMedia {
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
    medias = input.required<Map<string, Media>>();
    showDetails = input(false, {transform: booleanAttribute});
    editMode = input(false, {transform: booleanAttribute});
    allowEdit = input(false, {transform: booleanAttribute});  // shows edit button if true
    allowDuplicate = input(false, {transform: booleanAttribute});  // shows duplicate button if true
    allowHide = input(false, {transform: booleanAttribute});  // shows hide and show (eye) buttons if true
    editResult = output<string|null|undefined>();

    overrideDetails: boolean = false;
    editActive: boolean = false;
    variables: Map<string, variableDef> = new Map<string, variableDef>;
    till: Date | null = null;
    selectableTemplates: selectableTemplate[] = [];
    selectableLoops: selectableLoop[] = [];
    selectableUsers: selectableUser[] = [];
    selectableMedias: Map<string, selectableMedia[]> = new Map<string, selectableMedia[]>;

    constructor(
        private screenService: ScreenService,
        private userService: UserService
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
            let sm: Map<string, selectableMedia[]> = new Map<string, selectableMedia[]>;
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
                if (o.type.startsWith('media')) {
                    let sml: selectableMedia[] = [];
                    let media_types: number[] = [];
                    for (let mts of o.type.replace('media', '')) media_types.push(parseInt(mts));
                    if (media_types.length == 0) media_types = [0, 1, 2];
                    for (let media of this.medias().values()) {
                        if (media_types.includes(media.type)) sml.push(<selectableMedia>{code: media.id, name: media.desc})
                    }
                    sm.set(key, sml);
                }
                v.set(key, o);
            }
            this.variables = v;
            this.selectableMedias = sm;
        }
        if (this.screen().till != null) this.till = new Date(this.screen().till! * 1000);
        else this.till = null;
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
        if (this.till != null) this.screen().till = Math.floor(this.till.getTime() / 1000);
        else this.screen().till = null;
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

    hideScreen() {
        if (this.currentUser().id && this.screen().id) this.userService.addHide(this.currentUser().id!, this.screen().id!).subscribe();
    }

    unhideScreen() {
        if (this.currentUser().id && this.screen().id) this.userService.delHide(this.currentUser().id!, this.screen().id!).subscribe();
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
        let s: Screen = <Screen>{desc: cs.desc + ' - duplicate', template_id: cs.template_id, user_id: this.currentUser().id, duration: cs.duration, repeat: cs.repeat, loop: cs.loop, variables: cs.variables};
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
