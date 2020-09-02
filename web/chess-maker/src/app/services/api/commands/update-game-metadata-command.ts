import {Player, PlayerService} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {GameMetadata} from "../../game/game.service";
import {Color} from "../../color/color.service";
import {PackService} from "../../pack/pack.service";
import {Command} from "../command.service";

export type RawUpdateGameMetadataParameters = {
    game_metadata: {[id: string]: {
        display_name: string;
        creator: string;
        controller_pack_id: string;
        controller_id: string;
        players: {[id: number]: string};
    }};
};

export type UpdateGameMetadataParameters = {
    games: {[key: string]: GameMetadata};
};

@Injectable({providedIn: 'root'})
export class UpdateGameMetadataCommand extends Command<RawUpdateGameMetadataParameters, UpdateGameMetadataParameters> {
    constructor(
        private playerService: PlayerService,
        private packService: PackService,
    ) {
        super();
    }

    parse = (parameters: RawUpdateGameMetadataParameters): UpdateGameMetadataParameters => {
        const games: {[key: string]: GameMetadata} = {};

        for (const [id, rawGame] of Object.entries(parameters.game_metadata)) {
            const players: {[color in Color]?: Player} = {};

            for (const [color, playerId] of Object.entries(rawGame.players)) {
                players[color] = this.playerService.get(playerId);
            }

            games[id] = new GameMetadata(
                rawGame.display_name,
                this.playerService.get(rawGame.creator),
                this.packService.getController(rawGame.controller_pack_id, rawGame.controller_id),
                players,
            );
        }

        return {games};
    };
}
