import {EventEmitter, Injectable} from '@angular/core';
import {Player} from "../player/player.service";
import {CommandService, Subjects} from "../api/command.service";
import {ReceiveServerChatParameters} from "../api/commands/receive-server-chat-command";

export class ChatMessage {
    constructor(
        public sender: Player,
        public text: string,
    ) {}
}

@Injectable({
    providedIn: 'root',
})
export class ChatService {
    serverMessages: ChatMessage[] = [];
    scrollToBottom = new EventEmitter();

    constructor(commandService: CommandService) {
        commandService.ready.subscribe((subjects: Subjects) => {
            subjects.receiveServerChat.subscribe(this.receiveChatMessage);
        });
    }

    private receiveChatMessage = (parameters: ReceiveServerChatParameters): void => {
        this.serverMessages.push(new ChatMessage(parameters.player, parameters.text));
        this.scrollToBottom.emit();
    }
}
