export type RawDecorators = {[layer: number]: {
    row: number,
    col: number,
    pack_id: string,
    decorator_type_id: string,
}[]}

type RawInfoElements = {
    type: string,
    text: string,
    id?: string,
}[]

type RawInventoryItems = {
    id: string,
    pack_id: string,
    piece_type_id: string,
    color: number,
    direction: number,
    label: string,
}[]

type RawPly = {
    name: string,
    actions: {
        type: string,
        to_pos_row: number,
        to_pos_col: number,
        from_pos_row?: number,
        from_pos_col?: number,
        piece?: {
            pack_id: string,
            piece_type_id: string,
            color: number,
            direction: number,
        },
    }[],
}

export type RawSetPlayerParameters = {
    id: string,
}

export type RawFocusGameParameters = {
    game_id: string,
}

export type RawUpdatePackDataParameters = {
    packs: {[id: string]: {
        display_name: string,
        controllers: {[id: string]: {
            display_name: string,
            rows: number,
            cols: number,
            colors: number[],
            options: {[id: string]: any},
        }},
        pieces: {[id: string]: {
            image: string,
        }},
        decorators: {[id: string]: {
            image: string,
        }},
    }},
}

export type RawUpdatePlayersParameters = {
    players: {[id: string]: {
        display_name: string,
        active: boolean,
    }},
}

export type RawUpdateGameMetadataParameters = {
    game_metadata: {[id: string]: {
        display_name: string,
        creator: string,
        controller_pack_id: string,
        controller_id: string,
        players: {[id: number]: string},
    }},
}

export type RawFullGameDataParameters = {
    id: string,
    decorators: RawDecorators,
    public_info_elements: RawInfoElements,
    private_info_elements?: RawInfoElements,
    inventory_items: RawInventoryItems,
    pieces: {
        row: number,
        col: number,
        pack_id: string,
        piece_type_id: string,
        color: number,
        direction: number,
    }[],
    chat_messages: {
        sender_id: string,
        text: string,
    }[],
    winners?: {
        colors: number[],
        reason: string,
    },
}

export type RawUpdateDecoratorsParameters = {
    game_id: string,
    decorators: RawDecorators,
}

export type RawUpdateInfoElementsParameters = {
    game_id: string,
    info_elements: RawInfoElements,
    is_public: boolean,
}

export type RawUpdateInventoryItemsParameters = {
    game_id: string,
    inventory_items: RawInventoryItems,
}

export type RawApplyPlyParameters = {
    game_id: string,
    ply: RawPly,
}

export type RawUpdateWinnersParameters = {
    game_id: string,
    colors: number[],
    reason: string,
}

export type RawReceiveGameChatMessageParameters = {
    game_id: string,
    sender_id: string,
    text: string,
}

export type RawShowErrorParameters = {
    message: string,
}

export type RawOfferPliesParameters = {
    from_row: number,
    from_col: number,
    to_row: number,
    to_col: number,
    plies: RawPly[],
}

export type RawReceiveServerChatMessageParameters = {
    sender_id: string,
    text: string,
}
