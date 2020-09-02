import {Player, PlayerService} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {Command} from "../command.service";
import {RawInventoryItems} from "../parameter-types";
import {Game, GameService, InventoryItem} from "../../game/game.service";
import {PackService} from "../../pack/pack.service";

export type RawUpdateInventoryParameters = {
    game_id: string;
    inventory_items: RawInventoryItems;
};

export type UpdateInventoryParameters = {
    game: Game;
    inventoryItems: InventoryItem[];
};

@Injectable({providedIn: 'root'})
export class UpdateInventoryCommand extends Command<RawUpdateInventoryParameters, UpdateInventoryParameters> {
    constructor(
        private gameService: GameService,
        private packService: PackService,
    ) {
        super();
    }

    parse = (parameters: RawUpdateInventoryParameters): UpdateInventoryParameters => {
        const game = this.gameService.get(parameters.game_id);
        const inventoryItems = parameters.inventory_items.map(rawInventoryItem => new InventoryItem(
            rawInventoryItem.id,
            this.packService.getPieceType(rawInventoryItem.pack_id, rawInventoryItem.piece_type_id),
            rawInventoryItem.color,
            rawInventoryItem.direction,
            rawInventoryItem.label,
        ));

        return {game, inventoryItems};
    };
}
