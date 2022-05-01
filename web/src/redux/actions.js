export const PING_API = "PING_API";
export const SET_DOWNLOADS = "SET_DOWNLOADS";
export const SET_DOWNLOAD_PROGESS = "SET_DOWNLOAD_PROGESS";
export const SET_PREVIEW_INFO = "SET_PREVIEW_INFO";

export const setPreviewInfo = (payload) => {
    return { type: SET_PREVIEW_INFO, payload }
};
export const setDownloads = (payload) => {
    return { type: SET_DOWNLOADS, payload };
};
export const setDownloadProgress = (payload) => {
    return { type: SET_DOWNLOAD_PROGESS, payload};
}