import {Component, Inject} from "@angular/core";
import {ApiService} from "../../services/api/api.service";
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {Ply} from "../../services/game/game.service";
import {SelectPlyDialogData} from "../lobby.component";

@Component({
    selector: 'select-ply-dialog',
    templateUrl: 'select-ply-dialog.html',
})
export class SelectPlyDialog {
    constructor(
        public api: ApiService,
        @Inject(MAT_DIALOG_DATA) public data: SelectPlyDialogData,
    ) {}

    selectPly(ply: Ply): void {
        this.api.submitPly(
            this.data.game,
            this.data.from,
            this.data.to,
            ply,
        );
    }
}
