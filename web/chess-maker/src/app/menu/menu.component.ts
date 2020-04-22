import {Component, OnInit} from '@angular/core';
import {ApiService} from '../api.service';
import {Router} from '@angular/router';

@Component({
    selector: 'app-menu',
    templateUrl: './menu.component.html',
    styleUrls: ['./menu.component.less']
})
export class MenuComponent implements OnInit {
    address: string = 'localhost:8000';

    constructor(
        private apiService: ApiService,
        private router: Router,
    ) {}

    ngOnInit(): void {
    }

    connect() {
        this.apiService.connect(this.address);
        this.router.navigate(['/lobby']);
    }
}
