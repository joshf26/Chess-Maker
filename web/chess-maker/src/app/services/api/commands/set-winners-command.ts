import {Injectable} from "@angular/core";
import {Game, GameService, WinnerData} from "../../game/game.service";
import {Command} from "../command.service";

export type RawSetWinnersParameters = {
    game_id: string;
    colors: number[];
    reason: string;
};

export type SetWinnersParameters = {
    game: Game;
    winnerData: WinnerData;
};

@Injectable({providedIn: 'root'})
export class SetWinnersCommand extends Command<RawSetWinnersParameters, SetWinnersParameters> {
    constructor(private gameService: GameService) {
        super();
    }

    parse = (parameters: RawSetWinnersParameters): SetWinnersParameters => {
        const game = this.gameService.get(parameters.game_id);
        const winnerData = new WinnerData(parameters.colors, parameters.reason);

        return {game, winnerData};
    };
}
