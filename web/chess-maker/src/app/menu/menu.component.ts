import {Component, OnInit} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {Router} from '@angular/router';

@Component({
    selector: 'app-menu',
    templateUrl: './menu.component.html',
    styleUrls: ['./menu.component.less'],
})
export class MenuComponent implements OnInit {
    address: string = 'localhost:8000';
    displayName: string = 'Josh';

    constructor(
        private apiService: ApiService,
        private router: Router,
    ) {}

    ngOnInit(): void {}

    connect() {
        this.apiService.connect(this.address, this.displayName);
        this.router.navigate(['/lobby']);
    }
}
