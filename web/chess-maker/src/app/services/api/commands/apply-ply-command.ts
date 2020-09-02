import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {RawPly} from "../parameter-types";
import {Action, Game, GameService, Ply, Vector2} from "../../game/game.service";
import {PackService} from "../../pack/pack.service";

export type RawApplyPlyParameters = {
    game_id: string,
    ply: RawPly,
};

export type ApplyPlyParameters = {
    game: Game;
    ply: Ply;
};

@Injectable({providedIn: 'root'})
export class ApplyPlyCommand extends Command<RawApplyPlyParameters, ApplyPlyParameters> {
    constructor(
        private gameService: GameService,
        private packService: PackService,
    ) {
        super();
    }

    parse = (parameters: RawApplyPlyParameters): ApplyPlyParameters => {
        const game = this.gameService.get(parameters.game_id);
        const actions = parameters.ply.actions.map(rawAction => new Action(
            rawAction.type,
            new Vector2(rawAction.to_pos_row, rawAction.to_pos_col),
            rawAction.from_pos_row != undefined ? new Vector2(rawAction.from_pos_row, rawAction.from_pos_col) : undefined,
            rawAction.piece != undefined ? this.packService.getPieceType(rawAction.piece.pack_id, rawAction.piece.piece_type_id) : undefined,
            rawAction.piece != undefined ? rawAction.piece.color : undefined,
            rawAction.piece != undefined ? rawAction.piece.direction : undefined,
        ));
        const ply = new Ply(parameters.ply.name, actions);

        return {game, ply};
    };
}
