import {Injectable} from '@angular/core';
import {GameService} from "../game/game.service";
import {CommandService, Subjects} from "../api/command.service";

@Injectable({providedIn: 'root'})
export class UrlService {
    private gameIdToJoin?: string;

    constructor(
        private commandService: CommandService,
        private gameService: GameService,
    ) {
        commandService.ready.subscribe((subjects: Subjects) => {
            subjects.updateGameMetadata.subscribe(this.join);
        });
    }

    private join = (): void => {
        if (!this.gameIdToJoin) return;

        this.commandService.subjects.focusGame.next({
            game: this.gameService.get(this.gameIdToJoin),
        });
    };

    joinWhenReady(gameId: string): void {
        this.gameIdToJoin = gameId;
    }
}
