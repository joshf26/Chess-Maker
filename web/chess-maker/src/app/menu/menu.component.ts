import {Component, OnInit} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {Router} from '@angular/router';
import {PreferencesService} from "../services/preferences/preferences.service";
import {MatSnackBar} from "@angular/material/snack-bar";

@Component({
    selector: 'app-menu',
    templateUrl: './menu.component.html',
    styleUrls: ['./menu.component.less'],
})
export class MenuComponent implements OnInit {
    constructor(
        public preferencesService: PreferencesService,
        private apiService: ApiService,
        private router: Router,
        private snackBar: MatSnackBar,
    ) {}

    ngOnInit(): void {}

    connect() {
        this.snackBar.dismiss();
        this.apiService.connect(this.preferencesService.address, this.preferencesService.displayName);
        this.router.navigate(['/lobby']);
    }
}
