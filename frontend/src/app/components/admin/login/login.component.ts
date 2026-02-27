import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { IftaLabelModule } from 'primeng/iftalabel';
import { ButtonModule } from 'primeng/button';
import { Login } from '../../../interfaces/login';
import { LoginService } from '../../../services/login.service';
import { Router } from '@angular/router';
import { UserService } from '../../../services/user.service';
import { User } from '../../../interfaces/user';

@Component({
  selector: 'app-login',
  imports: [FormsModule, InputTextModule, PasswordModule, IftaLabelModule, ButtonModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {
    login?: Login;
    username: string = "";
    password: string = "";

    constructor(
        private loginService: LoginService,
        private userService: UserService,
        private router: Router
    ) { }

    ngOnInit(): void {
        this.refreshLogin();
    }

    refreshLogin() {
        this.loginService
            .getLogin()
            .subscribe((login: Login) => {
                this.login = login;
                if (login.complete) this.router.navigate(['/admin']);
            })
    }

    sendLogin() {
        this.loginService
            .startLogin(this.username)
            .subscribe((login: Login) => {
                this.login = login;
                if (login.session_id) {
                    this.loginService
                        .completeLogin(login.session_id, this.password)
                        .subscribe((login: Login) => {
                            this.login = login;
                            if (login.complete) {
                                this.userService.getMe().subscribe({
                                    next: (user: User) => {
                                        if (user.streamer) this.router.navigate(['/streamer']);
                                        else this.router.navigate(['/admin']);
                                    },
                                    error: () => {
                                        this.router.navigate(['/admin']);
                                    }
                                });
                            }
                        })
                }
            })
    }
}
