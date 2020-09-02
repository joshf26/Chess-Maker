import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {RawPly} from "../parameter-types";
import {Action, Direction, Ply, Vector2} from "../../game/game.service";
import {PackService, PieceType} from "../../pack/pack.service";
import {Color} from "../../color/color.service";

export type RawOfferPliesParameters = {
    from_row: number;
    from_col: number;
    to_row: number;
    to_col: number;
    plies: RawPly[];
};

export type OfferPliesParameters = {
    from: Vector2;
    to: Vector2;
    plies: Ply[];
};

@Injectable({providedIn: 'root'})
export class OfferPliesCommand extends Command<RawOfferPliesParameters, OfferPliesParameters> {
    constructor(private packService: PackService) {
        super();
    }

    parse = (parameters: RawOfferPliesParameters): OfferPliesParameters => {
        const from = new Vector2(parameters.from_row, parameters.from_col);
        const to = new Vector2(parameters.to_row, parameters.to_col);

        const plies: Ply[] = [];

        for (const rawPly of parameters.plies) {
            const actions: Action[] = [];

            for (const rawAction of rawPly.actions) {
                let actionFrom: Vector2 | null = null;
                let actionPieceType: PieceType | null = null;
                let actionColor: Color | null = null;
                let actionDirection: Direction | null = null;

                if (rawAction.type == 'create') {
                    actionPieceType = this.packService.getPieceType(rawAction.piece.pack_id, rawAction.piece.piece_type_id);
                    actionColor = rawAction.piece.color;
                    actionDirection = rawAction.piece.direction;
                }
                else if (rawAction.type == 'move') {
                    actionFrom = new Vector2(rawAction.from_pos_row, rawAction.from_pos_col);
                }

                actions.push(new Action(
                    rawAction.type,
                    new Vector2(rawAction.to_pos_row, rawAction.to_pos_col),
                    actionFrom,
                    actionPieceType,
                    actionColor,
                    actionDirection,
                ));
            }

            plies.push(new Ply(
                rawPly.name,
                actions,
            ));
        }

        return {from, to, plies};
    };
}
