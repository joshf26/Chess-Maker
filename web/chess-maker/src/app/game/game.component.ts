import {Component, EventEmitter, Input, Output, ViewChild} from '@angular/core';
import {Direction, Game, InfoElement} from "../services/game/game.service";
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
    @Input('game') game: Game;
    @Input('infoElements') infoElements: InfoElement[];
    @Output('toggleSidebar') toggleSidebar = new EventEmitter();
    @ViewChild('board') board: BoardComponent;

    direction: Direction = Direction.NORTH;

    constructor(
        public playerService: PlayerService,
        public apiService: ApiService,
        public sanitizer: DomSanitizer,
        public sidebarService: SidebarService,
    ) {}

    rotateBoardLeft() {
        this.direction = (this.direction + 7) % 8;
    }

    rotateBoardRight() {
        this.direction = (this.direction + 1) % 8;
    }

    centerBoard() {
        this.board.updateAndCenter();
    }

    move(move: Move) {
        this.apiService.plies(this.game, move.from, move.to);
    }

    place(place: Place) {
        this.apiService.inventoryPlies(this.game, place.item, place.to);
    }

    leaveGame(): void {
        this.apiService.leaveGame(this.game);
    }
}
