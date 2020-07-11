import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Game, GameService} from "../../services/game/game.service";
import {ApiService} from "../../services/api/api.service";

@Component({
    selector: 'app-games-list',
    templateUrl: './games-list.component.html',
    styleUrls: ['./games-list.component.less'],
})
export class GamesListComponent implements OnInit {
    @Input('selectedGame') selectedGame: Game;
    @Output() newGame = new EventEmitter();
    @Output() showGame = new EventEmitter<Game | undefined>();
    @Output() deleteGame = new EventEmitter<Game>();

    constructor(
        public gameService: GameService,
        public apiService: ApiService,
    ) {}

    ngOnInit(): void {}
}
