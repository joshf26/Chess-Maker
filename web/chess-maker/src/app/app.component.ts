import {Component} from '@angular/core';
import {ApiService} from './api.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.less']
})
export class AppComponent {
    COMMANDS = [
        {
            label: 'Create Standard8x8',
            command: 'create_game',
            parameters: {
                pack: 'standard',
                board: 'Standard8x8',
            },
        },
        {
            label: 'Join Game',
            command: 'join_game',
            parameters: {
                game_id: '',
                color: 0,
            },
        },
    ]


    constructor(private api: ApiService) {}

    submit(command: string, parameters: {[key: string]: any}) {
        this.api.run(command, parameters);
    }
}
