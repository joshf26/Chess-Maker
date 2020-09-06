import {Component, OnInit} from '@angular/core';
import {ApiService} from '../services/api/api.service';
import {ActivatedRoute, Router} from '@angular/router';
import {PreferencesService} from "../services/preferences/preferences.service";
import {MatSnackBar} from "@angular/material/snack-bar";
import {UrlService} from "../services/url/url.service";

@Component({
    selector: 'app-menu',
    templateUrl: './menu.component.html',
    styleUrls: ['./menu.component.less'],
})
export class MenuComponent implements OnInit {
    gameIdToJoin?: string = undefined;
    joinGameFromLink = true;

    constructor(
        public preferencesService: PreferencesService,
        private apiService: ApiService,
        private router: Router,
        private snackBar: MatSnackBar,
        private activatedRoute: ActivatedRoute,
        private urlService: UrlService,
    ) {}

    ngOnInit(): void {
        this.gameIdToJoin = this.activatedRoute.snapshot.queryParams['join'];
    }

    connect() {
        this.snackBar.dismiss();
        this.apiService.connect(this.preferencesService.address, this.preferencesService.displayName);
        this.router.navigate(['/lobby']).then(() => {
            if (this.gameIdToJoin && this.joinGameFromLink) {
                this.urlService.joinWhenReady(this.gameIdToJoin);
            }
        });
    }
}
