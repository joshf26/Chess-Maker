import {Component, ViewChild} from '@angular/core';
import {ChatService} from "../../services/chat/chat.service";
import {Game, GameService} from "../../services/game/game.service";
import {ApiService} from "../../services/api/api.service";
import {ChatBoxComponent} from "./chat-box/chat-box.component";

@Component({
    selector: 'app-chat',
    templateUrl: './chat.component.html',
    styleUrls: ['./chat.component.less'],
})
export class ChatComponent {
    @ViewChild('serverChatBox') serverChatBox: ChatBoxComponent;
    @ViewChild('gameChatBox') gameChatBox: ChatBoxComponent;

    selectedTab = 0;

    constructor(
        public gameService: GameService,
        public chatService: ChatService,
        public apiService: ApiService,
    ) {
        chatService.scrollToBottom.subscribe(() => {
            this.serverChatBox.scrollToBottom();
        });

        gameService.scrollToBottom.subscribe((game: Game) => {
            if (game == gameService.selectedGame) {
                this.gameChatBox.scrollToBottom();
            }
        });
    }
}
