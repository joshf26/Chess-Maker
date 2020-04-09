import {Component} from '@angular/core';
import {webSocket} from 'rxjs/webSocket';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.less']
})
export class AppComponent {
    constructor() {
        const socket = webSocket('ws://localhost:8000');

        socket.subscribe(
            console.log,
            console.error,
        );

        socket.next({
            command: 'create_game',
            parameters: {
                player1: 'Alice',
                player2: 'Bob',
            }
        });
    }
}
