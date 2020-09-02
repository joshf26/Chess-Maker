import {Injectable} from "@angular/core";
import {SetPlayerParameters} from "./commands/set-player-command";
import {UpdatePlayersParameters} from "./commands/update-players-command";
import {UpdatePackDataParameters} from "./commands/update-pack-data-command";
import {UpdateGameMetadataParameters} from "./commands/update-game-metadata-command";
import {FocusGameParameters} from "./commands/focus-game-command";
import {Subject} from "rxjs";
import {UpdateGameDataParameters} from "./commands/update-game-data-command";
import {UpdateDecoratorsParameters} from "./commands/update-decorators-command";
import {UpdateInfoParameters} from "./commands/update-info-command";
import {UpdateInventoryParameters} from "./commands/update-inventory-command";
import {ApplyPlyParameters} from "./commands/apply-ply-command";
import {SetWinnersParameters} from "./commands/set-winners-command";
import {ReceiveGameChatParameters} from "./commands/receive-game-chat-command";
import {ReceiveServerChatParameters} from "./commands/receive-server-chat-command";
import {OfferPliesParameters} from "./commands/offer-plies-command";
import {ShowErrorParameters} from "./commands/show-error-command";

export type Subjects = {
    setPlayer: Subject<SetPlayerParameters>;
    focusGame: Subject<FocusGameParameters>;
    updatePlayers: Subject<UpdatePlayersParameters>;
    updatePackData: Subject<UpdatePackDataParameters>;
    updateGameMetadata: Subject<UpdateGameMetadataParameters>;
    updateGameData: Subject<UpdateGameDataParameters>;
    updateDecorators: Subject<UpdateDecoratorsParameters>;
    updateInfo: Subject<UpdateInfoParameters>;
    updateInventory: Subject<UpdateInventoryParameters>;
    applyPly: Subject<ApplyPlyParameters>;
    setWinners: Subject<SetWinnersParameters>;
    receiveGameChat: Subject<ReceiveGameChatParameters>;
    receiveServerChat: Subject<ReceiveServerChatParameters>;
    offerPlies: Subject<OfferPliesParameters>;
    showError: Subject<ShowErrorParameters>;
};

export abstract class Command<R, P> {
    subject = new Subject<P>();

    run = (parameters: R): void => {
        this.subject.next(this.parse(parameters));
    };

    abstract parse(parameters: R): P;
}

@Injectable({providedIn: 'root'})
export class CommandService {
    private subjects?: Subjects;

    ready = new Subject<Subjects>();

    setSubjects(subjects: Subjects): void {
        this.subjects = subjects;

        this.ready.next(subjects);
    }
}
