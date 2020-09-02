import {Injectable} from "@angular/core";
import {Controller, DecoratorType, Pack, PieceType} from "../../pack/pack.service";
import {Vector2} from "../../game/game.service";
import {Command} from "../command.service";

export type RawUpdatePackDataParameters = {
    packs: {[id: string]: {
        display_name: string;
        controllers: {[id: string]: {
            display_name: string;
            rows: number;
            cols: number;
            colors: number[];
            options: {[id: string]: any};
        }};
        pieces: {[id: string]: {
            image: string;
        }};
        decorators: {[id: string]: {
            image: string;
        }};
    }};
};

export type UpdatePackDataParameters = {
    packs: {[key: string]: Pack};
};

@Injectable({providedIn: 'root'})
export class UpdatePackDataCommand extends Command<RawUpdatePackDataParameters, UpdatePackDataParameters> {
    parse = (parameters: RawUpdatePackDataParameters): UpdatePackDataParameters => {
        const packs: {[key: string]: Pack} = {};

        for (const [packId, rawPack] of Object.entries(parameters.packs)) {
            packs[packId] = new Pack(
                packId,
                rawPack.display_name,
                {},
                {},
                {},
            );

            for (const [controllerId, controller] of Object.entries(rawPack.controllers)) {
                packs[packId].controllers[controllerId] = new Controller(
                    controllerId,
                    controller.display_name,
                    packs[packId],
                    new Vector2(controller.rows, controller.cols),
                    controller.colors,
                    controller.options,
                );
            }

            for (const [pieceTypeId, pieceType] of Object.entries(rawPack.pieces)) {
                packs[packId].pieceTypes[pieceTypeId] = new PieceType(
                    pieceTypeId,
                    packs[packId],
                    pieceType.image,
                );
            }

            for (const [decoratorTypeId, decoratorType] of Object.entries(rawPack.decorators)) {
                packs[packId].decoratorTypes[decoratorTypeId] = new DecoratorType(
                    decoratorTypeId,
                    packs[packId],
                    decoratorType.image,
                );
            }
        }

        return {packs};
    };
}
