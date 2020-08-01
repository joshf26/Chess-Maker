import {ChangeDetectorRef, Component, EventEmitter, Input, Output, ViewChild} from '@angular/core';
import {Direction, Game, GameService, InfoElement} from "../services/game/game.service";
import {PlayerService} from "../services/player/player.service";
import {ApiService} from "../services/api/api.service";
import {DomSanitizer} from "@angular/platform-browser";
import {BoardComponent, Move, Place} from "./board/board.component";
import {SidebarService} from "../services/sidebar/sidebar.service";

@Component({
    selector: 'app-game',
    templateUrl: './game.component.html',
    styleUrls: ['./game.component.less'],
})
export class GameComponent {
    @Input() game: Game;
    @Input() infoElements: InfoElement[];
    @Output() toggleSidebar = new EventEmitter();
    @ViewChild('board') board: BoardComponent;

    direction: Direction = Direction.NORTH;

    constructor(
        private gameService: GameService,
        public playerService: PlayerService,
        public apiService: ApiService,
        public sanitizer: DomSanitizer,
        public sidebarService: SidebarService,
    ) {
        this.gameService.updateBoard.subscribe(() => this.board.ngOnChanges({}));
    }

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
