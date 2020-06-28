import {Component, Input} from '@angular/core';
import {Color, ColorService} from "../services/color/color.service";
import {Player} from "../services/player/player.service";

@Component({
    selector: 'app-players',
    templateUrl: './players.component.html',
    styleUrls: ['./players.component.less'],
})
export class PlayersComponent {
    @Input('serverPlayers') serverPlayers: Player[];
    @Input('gamePlayers') gamePlayers: {[color in Color]?: Player};
    @Input('disableGameTab') disableGameTab: boolean;

    selectedTab: number = 0;

    constructor(
        public colorService: ColorService,
    ) {}

    hasPlayers() {
        return Object.keys(this.gamePlayers).length > 0;
    }
}
