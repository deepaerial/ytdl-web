import { mapDownloads } from './utils'

import { ACTION } from './constants';

export const downloadsReducer = (downloads, action) => {
    switch (action.type) {
        case ACTION.FETCH_ALL: {
            const fetchedDownloads = mapDownloads(action.downloads);
            return fetchedDownloads;
        }
        case ACTION.STATUS_UPDATE: {
            const downloadsCopy = { ...downloads }
            let downloadItem = downloadsCopy[action.mediaId];
            if (downloadItem) {
                downloadItem = Object.assign(downloadItem, {
                    status: action.status, progress: action.progress
                });
                downloadsCopy[media_id] = downloadItem;
                return downloadsCopy;
            }
            break;
        }
        // TODO:  Add action for deleting deonwload from list
        default:
            throw Error(`Unknown action ${action.type}`);
    }
}