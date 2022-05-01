import { SET_DOWNLOADS, SET_DOWNLOAD_PROGESS } from "./actions";
import { mapDownloads } from "../utils";

const initialState = {
    api_version: null,
    downloads: {},
    isLoading: false
};

const rootReducer = (state = initialState, {type, payload}) => {
    switch (type) {
        case SET_DOWNLOADS:
            downloads = mapDownloads(payload);
            return Object.assign({}, state, { downloads });
        default:
            return state
    }
}
export default rootReducer;
