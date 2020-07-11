import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Game, GameService} from "../../services/game/game.service";
import {ApiService} from "../../services/api/api.service";
import {PlayerService} from "../../services/player/player.service";

@Component({
    selector: 'app-games-list',
    templateUrl: './games-list.component.html',
    styleUrls: ['./games-list.component.less'],
})
export class GamesListComponent implements OnInit {
    @Input() loading = false;
    @Output() newGame = new EventEmitter();
    @Output() showGame = new EventEmitter<Game | undefined>();
    @Output() leaveGame = new EventEmitter<Game>();
    @Output() deleteGame = new EventEmitter<Game>();

    selectedTab: number = 0;

    constructor(
        public gameService: GameService,
        public apiService: ApiService,
        public playerService: PlayerService,
    ) {}

    ngOnInit(): void {}
}
