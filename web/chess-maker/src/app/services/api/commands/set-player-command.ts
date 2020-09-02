import {Player, PlayerService} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {Command} from "../command.service";

export type RawSetPlayerParameters = {
    id: string;
};

export type SetPlayerParameters = {
    player: Player;
};

@Injectable({providedIn: 'root'})
export class SetPlayerCommand extends Command<RawSetPlayerParameters, SetPlayerParameters> {
    constructor(private playerService: PlayerService) {
        super();
    }

    parse = (parameters: RawSetPlayerParameters): SetPlayerParameters => {
        const player = this.playerService.get(parameters.id);

        return {player};
    };
}
