import {EventEmitter, Injectable} from '@angular/core';
import {Player} from "../player/player.service";

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

    constructor() {}

    receiveChatMessage(sender: Player, text: string): void {
        this.serverMessages.push(new ChatMessage(sender, text));
        this.scrollToBottom.emit();
    }
}
