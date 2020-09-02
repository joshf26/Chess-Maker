import {Injectable} from '@angular/core';
import {Identifiable, ItemService} from "../item-service";
import {SetPlayerParameters} from "../api/commands/set-player-command";
import {UpdatePlayersParameters} from "../api/commands/update-players-command";
import {Subjects, CommandService} from "../api/command.service";

export class Player implements Identifiable {
    constructor(
        public id: string,
        public displayName: string,
        public active: boolean,
    ) {}
}

@Injectable({providedIn: 'root'})
export class PlayerService extends ItemService<Player> {
    constructor(commandService: CommandService) {
        super();

        commandService.ready.subscribe((subjects: Subjects) => {
            subjects.setPlayer.subscribe(this.setPlayer);
            subjects.updatePlayers.subscribe(this.updatePlayers);
        });
    }

    currentPlayer: Player | undefined;

    private setPlayer = (parameters: SetPlayerParameters): void => {
        this.currentPlayer = parameters.player;
    };

    private updatePlayers = (parameters: UpdatePlayersParameters): void => {
        this.items = parameters.players;

        if (this.currentPlayer) {
            this.currentPlayer = parameters.players[this.currentPlayer.id];
        }
    };
}
