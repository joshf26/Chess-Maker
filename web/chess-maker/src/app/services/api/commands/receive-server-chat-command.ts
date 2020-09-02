import {Player, PlayerService} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {ChatMessage} from "../../chat/chat.service";
import {Game, GameService} from "../../game/game.service";

export type RawReceiveServerChatParameters = {
    sender_id: string;
    text: string;
};

export type ReceiveServerChatParameters = {
    player: Player;
    text: string;
};

@Injectable({providedIn: 'root'})
export class ReceiveServerChatCommand extends Command<RawReceiveServerChatParameters, ReceiveServerChatParameters> {
    constructor(
        private gameService: GameService,
        private playerService: PlayerService,
    ) {
        super();
    }

    parse = (parameters: RawReceiveServerChatParameters): ReceiveServerChatParameters => {
        const player = this.playerService.get(parameters.sender_id);
        const text = parameters.text;

        return {player, text};
    };
}
