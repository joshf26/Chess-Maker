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

export type RawUpdateGameDataParameters = {
    id: string,
    pieces: {
        row: number,
        col: number,
        pack_id: string,
        piece_type_id: string,
        color: number,
        direction: number,
    }[],
    decorators: {
        row: number,
        col: number,
        pack_id: string,
        decorator_type_id: string,
    }[],
    info_elements: {
        type: string,
        text: string,
        id?: string,
    }[],
    inventory_items: {
        id: string,
        pack_id: string,
        piece_type_id: string,
        color: number,
        direction: number,
        label: string,
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

export type RawDoPly = {
    ply: RawPly,
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
