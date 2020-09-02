import {Component, EventEmitter, Input, Output, ViewChild} from '@angular/core';
import {Direction, Game, GameService, InfoElement} from "../services/game/game.service";
import {PlayerService} from "../services/player/player.service";
import {ApiService} from "../services/api/api.service";
import {BoardComponent, Move, Place} from "./board/board.component";
import {SidebarService} from "../services/sidebar/sidebar.service";
import {RawShowErrorParameters} from "../services/api/parameter-types";
import {MatSnackBar} from "@angular/material/snack-bar";
import {CommandService, Subjects} from "../services/api/command.service";

@Component({
    selector: 'app-game',
    templateUrl: './game.component.html',
    styleUrls: ['./game.component.less'],
})
export class GameComponent {
    @Input() game: Game;
    @Input() publicInfoElements: InfoElement[];
    @Input() privateInfoElements: InfoElement[];
    @Output() toggleSidebar = new EventEmitter();
    @ViewChild('board') board: BoardComponent;

    direction: Direction = Direction.NORTH;

    constructor(
        private gameService: GameService,
        public playerService: PlayerService,
        public apiService: ApiService,
        public sidebarService: SidebarService,
        private snackBar: MatSnackBar,
        commandService: CommandService,
    ) {
        commandService.ready.subscribe((subjects: Subjects) => {
            subjects.showError.subscribe(this.showError);
        });
        this.gameService.updateBoard.subscribe(() => this.board.ngOnChanges({}));
    }

    private showError = (parameters: RawShowErrorParameters): void => {
        this.snackBar.open(parameters.message, 'Ok', {
            duration: 5000,
            horizontalPosition: 'end',
            panelClass: 'error',
        });
    };

    rotateBoardLeft() {
        this.game.renderData.direction = (this.game.renderData.direction + 7) % 8;
        this.centerBoard();
    }

    rotateBoardRight() {
        this.game.renderData.direction = (this.game.renderData.direction + 1) % 8;
        this.centerBoard();
    }

    centerBoard() {
        this.board.centerBoard();
    }

    move(move: Move) {
        this.apiService.plies(this.game, move.from, move.to);
    }

    place(place: Place) {
        this.apiService.inventoryPlies(this.game, place.item, place.to);
    }
}
