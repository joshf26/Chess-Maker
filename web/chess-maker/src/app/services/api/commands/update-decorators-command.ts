import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {RawDecorators} from "../parameter-types";
import {Decorator, Game, GameService} from "../../game/game.service";
import {PackService} from "../../pack/pack.service";

export type RawUpdateDecoratorsParameters = {
    game_id: string;
    decorators: RawDecorators;
};

export type UpdateDecoratorsParameters = {
    game: Game;
    decoratorLayers: {[layer: number]: Decorator[]};
};

@Injectable({providedIn: 'root'})
export class UpdateDecoratorsCommand extends Command<RawUpdateDecoratorsParameters, UpdateDecoratorsParameters> {
    constructor(
        private packService: PackService,
        private gameService: GameService,
    ) {
        super();
    }

    parse = (parameters: RawUpdateDecoratorsParameters): UpdateDecoratorsParameters => {
        const game = this.gameService.get(parameters.game_id);
        const decoratorLayers: {[layer: number]: Decorator[]} = {};
        this.packService.fillDecoratorLayers(parameters.decorators, decoratorLayers);

        return {game, decoratorLayers};
    };
}
