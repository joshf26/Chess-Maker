import {Injectable} from '@angular/core';
import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {filter} from 'rxjs/operators';

interface PieceData {
    id: number,
    image: string,
}

interface GameInitData {
    board_size_x: number,
    board_size_y: number,
    pieces: PieceData[],
}

interface TileData {
    piece_id?: number,
    color_id?: number,
}

interface GameUpdateData {
    move?: number,
    ply?: number,

    boardX?: number,
    boardY?: number,
    board?: TileData[][],
}

interface GameMetaData {
    name: string,
    creator: string,
    board: string,
    current_players: number,
    total_players: number,
}

@Injectable({
    providedIn: 'root',
})
export class ApiService {
    private socket: WebSocketSubject<unknown>;
    private commands: Observable<unknown>;
    private gameObservables: {[key: string]: Observable<GameUpdateData>}

    constructor(private router: Router) {}

    connect(address: string) {
        this.socket = webSocket(`ws://${address}`);
        this.commands = this.socket.pipe(
            filter(message => message.hasOwnProperty('command') && message.hasOwnProperty('parameters')),
        );

        this.commands.subscribe(
            message => {},
            error => {
                if (error instanceof CloseEvent) {
                    alert('The server has closed.')
                } else {
                    alert('Cannot reach the server.')
                }
                this.router.navigate(['/']);
            },
        );
    }

    getCommand(command: string): Observable<unknown> {
        return this.commands.pipe(
            filter(message => message['command'] == command),
        );
    }

    run(command: string, parameters: {[key: string]: any}): void {
        this.socket.next({
            command: command,
            parameters: parameters,
        });
    }
}
