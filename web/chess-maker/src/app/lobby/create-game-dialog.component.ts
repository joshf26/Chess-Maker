import {Component, Inject, ViewChild} from "@angular/core";
import {PackDataService} from "../services/pack-data/pack-data.service";
import {ApiService} from "../services/api/api.service";
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {CreateGameDialogData} from "./lobby.component";
import {MatSelectionList} from "@angular/material/list";

@Component({
    selector: 'create-game-dialog',
    templateUrl: 'create-game-dialog.component.html',
    styleUrls: ['./create-game-dialog.component.less'],
})
export class CreateGameDialog {
    constructor(
        public packDataService: PackDataService,
        public api: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: CreateGameDialogData,
    ) {
    }

    createGame(): void {
        this.api.run('create_game', {
            name: this.data.name,
            pack: this.data.board.pack,
            board: this.data.board.name,
        })
    }
}
