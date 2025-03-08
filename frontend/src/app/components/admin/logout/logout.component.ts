import { Component, OnInit } from '@angular/core';
import { LoginService } from '../../../services/login.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-logout',
  imports: [],
  templateUrl: './logout.component.html',
  styleUrl: './logout.component.scss'
})
export class LogoutComponent implements OnInit {

    constructor(
        private loginService: LoginService,
        private router: Router
    ) {}

    ngOnInit(): void {
        this.loginService
            .logout()
            .subscribe((something: any) => {
                this.router.navigate(['/login'])
            })
    }
}
