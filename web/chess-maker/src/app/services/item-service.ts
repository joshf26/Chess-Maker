export interface Identifiable {
    id: string;
}

export abstract class ItemService<T extends Identifiable> {
    protected items: {[id: string]: T} = {};

    get(id: string): T {
        return this.items[id];
    }

    values(): T[] {
        return Object.values(this.items);
    }
}
