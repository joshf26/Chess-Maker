import {Injectable} from '@angular/core';
import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import {Observable} from 'rxjs';
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

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private socket: WebSocketSubject<unknown>;
    private gameObservables: {[key: string]: Observable<GameUpdateData>}

    constructor() {
        this.socket = webSocket('ws://localhost:8000');
        this.socket.pipe(filter());
        this.socket.next('hello');
    }

    run(command: string, parameters: {[key: string]: any}): void {
        this.socket.next({
            command: command,
            parameters: parameters,
        });
    }

    addBoardObservable(gameId: string) {
        this.gameObservables[gameId] = new Observable<GameUpdateData>(observer => {
            this.socket.subscribe(console.log);
            observer.next()
        })
    }

    getBoard(gameId: string, startX: number, startY: number, width: number, height: number) {
        this.run('get_board', {
            game_id: gameId,
            start_x: startX,
            start_y: startY,
            width: width,
            height: height,
        })
    }
}
