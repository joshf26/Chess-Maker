import {Injectable} from '@angular/core';
import {Identifiable, ItemService} from "../item-service";

export class Player implements Identifiable {
    constructor(
        public id: string,
        public displayName: string,
    ) {}
}

@Injectable({
    providedIn: 'root',
})
export class PlayerService extends ItemService<Player> {
    currentPlayer: Player | undefined;

    updatePlayers(players: {[id: string]: Player}): void {
        this.items = players;

        if (this.currentPlayer) {
            this.currentPlayer = players[this.currentPlayer.id];
        }
    }

    setPlayer(player: Player): void {
        this.currentPlayer = player;
    }
}
