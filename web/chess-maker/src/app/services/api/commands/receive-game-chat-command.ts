import {PlayerService} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {ChatMessage} from "../../chat/chat.service";
import {Game, GameService} from "../../game/game.service";

export type RawReceiveGameChatParameters = {
    game_id: string;
    sender_id: string;
    text: string;
};

export type ReceiveGameChatParameters = {
    game: Game;
    chatMessage: ChatMessage;
};

@Injectable({providedIn: 'root'})
export class ReceiveGameChatCommand extends Command<RawReceiveGameChatParameters, ReceiveGameChatParameters> {
    constructor(
        private gameService: GameService,
        private playerService: PlayerService,
    ) {
        super();
    }

    parse = (parameters: RawReceiveGameChatParameters): ReceiveGameChatParameters => {
        const game = this.gameService.get(parameters.game_id);
        const sender = this.playerService.get(parameters.sender_id);
        const chatMessage = new ChatMessage(sender, parameters.text);

        return {game, chatMessage};
    };
}
