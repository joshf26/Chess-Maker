import {Component, Input} from '@angular/core';
import {Player} from "../../services/player/player.service";
import {Color, ColorService} from "../../services/color/color.service";

@Component({
    selector: 'app-players-list',
    templateUrl: './players-list.component.html',
    styleUrls: ['./players-list.component.less'],
})
export class PlayersListComponent {
    @Input() serverPlayers: Player[];
    @Input() gamePlayers: {[color in Color]?: Player};
    @Input() disableGameTab: boolean;

    selectedTab: number = 0;

    constructor(
        public colorService: ColorService,
    ) {}

    hasPlayers() {
        return Object.keys(this.gamePlayers).length > 0;
    }
}
