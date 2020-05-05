import {Injectable} from '@angular/core';
import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import {map, filter} from 'rxjs/operators';

@Injectable({
    providedIn: 'root',
})
export class ApiService {
    private socket: WebSocketSubject<unknown>;
    private commands: Observable<unknown>;

    constructor(private router: Router) {}

    connect(address: string) {
        this.socket = webSocket(`ws://${address}`);

        this.socket.pipe(
            filter(message => message.hasOwnProperty('error'))
        ).subscribe(console.error);

        this.commands = this.socket.pipe(
            filter(message => message.hasOwnProperty('command') && message.hasOwnProperty('parameters')),
        );

        this.commands.subscribe(
            console.log, //message => {},
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

    // TODO: This could be a decorator.
    getCommand(command: string): Observable<unknown> {
        if (this.commands == undefined) {
            // Command was queried before connection was established. Forward user back to login.
            this.router.navigate(['/']);
            return;
        }

        return this.commands.pipe(
            filter(message => message['command'] == command),
            map(message => message['parameters']),
        );
    }

    run(command: string, parameters: {[key: string]: any}): void {
        this.socket.next({
            command: command,
            parameters: parameters,
        });
    }
}
