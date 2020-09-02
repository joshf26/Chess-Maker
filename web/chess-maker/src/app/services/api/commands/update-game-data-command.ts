import {Player, PlayerService} from "../../player/player.service";
import {Injectable} from "@angular/core";
import {
    Decorator, GameData,
    GameMetadata,
    InfoElement,
    InventoryItem,
    Piece,
    PieceMap,
    Vector2,
    WinnerData
} from "../../game/game.service";
import {Color} from "../../color/color.service";
import {PackService} from "../../pack/pack.service";
import {Command} from "../command.service";
import {RawDecorators, RawInfoElements, RawInventoryItems} from "../parameter-types";
import {ChatMessage} from "../../chat/chat.service";

export type RawUpdateGameDataParameters = {
    id: string;
    decorators: RawDecorators;
    public_info_elements: RawInfoElements;
    private_info_elements?: RawInfoElements;
    inventory_items: RawInventoryItems;
    pieces: {
        row: number;
        col: number;
        pack_id: string;
        piece_type_id: string;
        color: number;
        direction: number;
    }[];
    chat_messages: {
        sender_id: string;
        text: string;
    }[];
    winners?: {
        colors: number[];
        reason: string;
    };
};

export type UpdateGameDataParameters = {
    id: string;
    data: GameData;
};

@Injectable({providedIn: 'root'})
export class UpdateGameDataCommand extends Command<RawUpdateGameDataParameters, UpdateGameDataParameters> {
    constructor(
        private playerService: PlayerService,
        private packService: PackService,
    ) {
        super();
    }

    parse = (parameters: RawUpdateGameDataParameters): UpdateGameDataParameters => {
        const pieces = new PieceMap();
        const decorators: {[layer: number]: Decorator[]} = [];
        const publicInfoElements: InfoElement[] = [];
        const inventoryItems: InventoryItem[] = [];
        const chatMessages: ChatMessage[] = [];
        let privateInfoElements: InfoElement[] | undefined = undefined;

        for (const rawPiece of parameters.pieces) {
            pieces.set(new Vector2(rawPiece.row, rawPiece.col), new Piece(
                this.packService.getPieceType(rawPiece.pack_id, rawPiece.piece_type_id),
                rawPiece.color,
                rawPiece.direction,
            ));
        }

        this.packService.fillDecoratorLayers(parameters.decorators, decorators);

        // TODO: Change these to map calls.
        for (const rawInfoElement of parameters.public_info_elements) {
            publicInfoElements.push(new InfoElement(
                rawInfoElement.type,
                rawInfoElement.text,
                rawInfoElement.id,
            ));
        }

        if (parameters.private_info_elements) {
            privateInfoElements = [];

            for (const rawInfoElement of parameters.private_info_elements) {
                privateInfoElements.push(new InfoElement(
                    rawInfoElement.type,
                    rawInfoElement.text,
                    rawInfoElement.id,
                ));
            }
        }

        for (const rawInventoryItem of parameters.inventory_items) {
            inventoryItems.push(new InventoryItem(
                rawInventoryItem.id,
                this.packService.getPieceType(rawInventoryItem.pack_id, rawInventoryItem.piece_type_id),
                rawInventoryItem.color,
                rawInventoryItem.direction,
                rawInventoryItem.label,
            ));
        }

        for (const rawChatMessage of parameters.chat_messages) {
            chatMessages.push(new ChatMessage(
                this.playerService.get(rawChatMessage.sender_id),
                rawChatMessage.text,
            ))
        }

        const winnerData = parameters.winners ? new WinnerData(parameters.winners.colors, parameters.winners.reason) : null;

        const id = parameters.id;
        const data = new GameData(
            pieces,
            decorators,
            publicInfoElements,
            privateInfoElements,
            inventoryItems,
            chatMessages,
            winnerData,
        );

        return {id, data};
    };
}
