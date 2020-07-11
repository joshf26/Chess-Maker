import {Component, Inject} from "@angular/core";
import {PackService} from "../../services/pack/pack.service";
import {ApiService} from "../../services/api/api.service";
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {CreateGameDialogData} from "../lobby.component";

@Component({
    selector: 'create-game-dialog',
    templateUrl: 'create-game-dialog.component.html',
    styleUrls: ['./create-game-dialog.component.less'],
})
export class CreateGameDialog {
    options: {[key: string]: any} = {};

    constructor(
        public packService: PackService,
        public apiService: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: CreateGameDialogData,
    ) {}

    updateOptions(): void {
        for (const [option, defaultValue] of Object.entries(this.data.controller.options)) {
            this.options[option] = defaultValue.default;
        }
    }

    createGame(): void {
        this.apiService.createGame(
            this.data.displayName,
            this.data.controller,
            this.options,
        );
    }

    isEmpty(object: any): boolean {
        return Object.keys(object).length == 0;
    }
}
