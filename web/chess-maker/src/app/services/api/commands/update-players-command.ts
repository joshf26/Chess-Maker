import {Player} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {Command} from "../command.service";

export type RawUpdatePlayersParameters = {
    players: {[id: string]: {
        display_name: string;
        active: boolean;
    }};
};

export type UpdatePlayersParameters = {
    players: {[key: string]: Player};
};

@Injectable({providedIn: 'root'})
export class UpdatePlayersCommand extends Command<RawUpdatePlayersParameters, UpdatePlayersParameters> {
    parse = (parameters: RawUpdatePlayersParameters): UpdatePlayersParameters => {
        const players: {[key: string]: Player} = {};

        for (const [playerId, rawPlayer] of Object.entries(parameters.players)) {
            players[playerId] = new Player(
                playerId,
                rawPlayer.display_name,
                rawPlayer.active,
            );
        }

        return {players};
    };
}
