import {Injectable} from "@angular/core";
import {Command} from "../command.service";

export type RawShowErrorParameters = {
    message: string,
};

export type ShowErrorParameters = {
    message: string,
};

@Injectable({providedIn: 'root'})
export class ShowErrorCommand extends Command<RawShowErrorParameters, ShowErrorParameters> {
    parse = (parameters: RawShowErrorParameters): ShowErrorParameters => {
        const message = parameters.message;

        return {message};
    };
}
