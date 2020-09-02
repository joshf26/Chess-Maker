export type RawDecorators = {[layer: number]: {
    row: number,
    col: number,
    pack_id: string,
    decorator_type_id: string,
}[]}

export type RawInfoElements = {
    type: string,
    text: string,
    id?: string,
}[]

export type RawInventoryItems = {
    id: string,
    pack_id: string,
    piece_type_id: string,
    color: number,
    direction: number,
    label: string,
}[]

export type RawPly = {
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

export type RawShowErrorParameters = {
    message: string,
}
