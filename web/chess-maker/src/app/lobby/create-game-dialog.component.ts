import {ChangeDetectorRef, Component, Inject} from "@angular/core";
import {PackDataService} from "../services/pack-data/pack-data.service";
import {ApiService} from "../services/api/api.service";
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {CreateGameDialogData} from "./lobby.component";

@Component({
    selector: 'create-game-dialog',
    templateUrl: 'create-game-dialog.component.html',
    styleUrls: ['./create-game-dialog.component.less'],
})
export class CreateGameDialog {
    options: {[key: string]: any} = {};

    constructor(
        public packDataService: PackDataService,
        public api: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: CreateGameDialogData,
    ) {
    }

    updateOptions(): void {
        for (const [option, defaultValue] of Object.entries(this.packDataService.boardTypes[this.data.board.pack][this.data.board.name].options)) {
            this.options[option] = defaultValue.default;
        }
    }

    createGame(): void {
        this.api.run('create_game', {
            name: this.data.name,
            pack: this.data.board.pack,
            board: this.data.board.name,
            options: this.options,
        })
    }

    isEmpty(object: any): boolean {
        return Object.keys(object).length == 0;
    }
}
