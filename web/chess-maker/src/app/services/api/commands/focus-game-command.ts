import {Injectable} from "@angular/core";
import {Game, GameService} from "../../game/game.service";
import {Command} from "../command.service";

export type RawFocusGameParameters = {
    game_id: string,
};

export type FocusGameParameters = {
    game: Game;
};

@Injectable({providedIn: 'root'})
export class FocusGameCommand extends Command<RawFocusGameParameters, FocusGameParameters> {
    constructor(private gameService: GameService) {
        super();
    }

    parse = (parameters: RawFocusGameParameters): FocusGameParameters => {
        const game = this.gameService.get(parameters.game_id);

        return {game};
    };
}
