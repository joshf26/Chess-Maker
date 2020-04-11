import {Component} from '@angular/core';
import {webSocket, WebSocketSubject} from 'rxjs/webSocket';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.less']
})
export class AppComponent {
    COMMANDS = [
        {
            label: 'Create Standard8x8',
            body: JSON.stringify({
                'command': 'create_game',
                'parameters': {
                    'pack': 'standard',
                    'board': 'Standard8x8',
                },
            }),
        },
        {
            label: 'Join Game',
            body: JSON.stringify({
                'command': 'join_game',
                'parameters': {
                    'game_id': '',
                    'color': 0,
                },
            }),
        },
    ]

    private socket: WebSocketSubject<unknown>;

    constructor() {
        this.socket = webSocket('ws://localhost:8000');

        this.socket.subscribe(
            console.log,
            console.error,
        );
    }

    submit(body: string) {
        this.socket.next(JSON.parse(body));
    }
}
