import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {Game, GameService, InfoElement} from "../../game/game.service";
import {RawInfoElements} from "../parameter-types";

export type RawUpdateInfoParameters = {
    game_id: string,
    info_elements: RawInfoElements,
    is_public: boolean,
};

export type UpdateInfoParameters = {
    game: Game;
    infoElements: InfoElement[];
    isPublic: boolean;
};

@Injectable({providedIn: 'root'})
export class UpdateInfoCommand extends Command<RawUpdateInfoParameters, UpdateInfoParameters> {
    constructor(private gameService: GameService) {
        super();
    }

    parse = (parameters: RawUpdateInfoParameters): UpdateInfoParameters => {
        const game = this.gameService.get(parameters.game_id);
        const infoElements = parameters.info_elements.map(rawInfoElement => new InfoElement(
            rawInfoElement.type,
            rawInfoElement.text,
            rawInfoElement.id,
        ));
        const isPublic = parameters.is_public;

        return {game, infoElements, isPublic};
    };
}
