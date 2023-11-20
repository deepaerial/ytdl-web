import { mapDownloads } from './utils'

import { ACTION, Statuses } from './constants';

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
                    status: action.status, progress: action.progress, filesizeHr: action.filesizeHr
                });
                downloadsCopy[action.mediaId] = downloadItem;
                return downloadsCopy;
            }
            return downloadsCopy;
        }
        case ACTION.DELETE: {
            const downloadsCopy = { ...downloads };
            if (action.status === Statuses.DELETED) {
                delete downloadsCopy[action.mediaId];
            }
            return downloadsCopy;
        }
        default:
            throw Error(`Unknown action ${action.type}`);
    }
}