import {ChangeDetectorRef, Component, ElementRef, EventEmitter, Input, Output, ViewChild} from '@angular/core';
import {ChatMessage} from "../../../services/chat/chat.service";

@Component({
    selector: 'app-chat-box',
    templateUrl: './chat-box.component.html',
    styleUrls: ['./chat-box.component.less']
})
export class ChatBoxComponent {
    @Input() messages: ChatMessage[];
    @Output() send = new EventEmitter<string>();
    @ViewChild('messagesContainer') messagesContainer: ElementRef;

    inputMessage: string;

    constructor(
        private changeDetectorRer: ChangeDetectorRef,
    ) {}

    sendMessage(): void {
        this.send.emit(this.inputMessage);
        this.inputMessage = '';
    }

    scrollToBottom(): void {
        if (!this.messagesContainer) {
            return;
        }

        // Ensure the new message is rendered before scrolling.
        this.changeDetectorRer.detectChanges();

        const messagesContainerElement = this.messagesContainer.nativeElement;
        messagesContainerElement.scrollTop = messagesContainerElement.scrollHeight;
    }
}
