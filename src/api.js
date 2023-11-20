import { getFilenameFromContentDisposition } from './utils'
import axios from 'axios';

export const apiURL = import.meta.env.VITE_API_URL;

const api = axios.create({ baseURL: apiURL, withCredentials: true });

export class API {

    static async getApiVersion() {
        try {
            const response = await api.get('version');
            return response.data;
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                error_message = exc.response.data.detail;
            } else if (exc.message) {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

    static async getPreview(url) {
        try {
            const response = await api.get('preview', { params: { url } });
            return response.data;
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                if (exc.response.status == 422) {
                    const error = exc.response.data.detail[0]
                    error_message = error.msg
                } else error_message = exc.response.data.detail;
            } else {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

    static async getDownloads() {
        try {
            const response = await api.get('downloads');
            return response.data["downloads"];
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                error_message = exc.response.data.detail;
            } else {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

    static async enqueueDownload(url, videoStream, audioStream, mediaFormat) {
        try {
            const response = await api.put('download', {
                url,
                videoStreamId: videoStream,
                audioStreamId: audioStream,
                mediaFormat
            });
            return response.data["downloads"];
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                error_message = exc.response.data.detail;
            } else {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

    static async fetchMediaInfo(videoUrl, mediaFormat) {
        try {
            const response = await api.put('fetch', {
                url: videoUrl,
                media_format: mediaFormat
            });
            return response.data.downloads;
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                const detail = exc.response.data.detail;
                if (typeof detail === 'string') {
                    error_message = detail;
                }
                else {
                    error_message = detail[0].msg;
                }
            } else {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

    static async downloadMediaFile(mediaId) {
        try {
            const params = { mediaId: mediaId }
            const response = await api.get('download', { params, responseType: 'blob' });
            const filename = getFilenameFromContentDisposition(response);
            const link = document.createElement('a');
            link.href = URL.createObjectURL(response.data);
            link.download = filename;
            link.click();
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                const data = exc.response.data;
                error_message = await new Promise((resolve, reject) => {
                    const fileReader = new FileReader();
                    fileReader.onload = (e) => {
                        const error = JSON.parse(e.target.result);
                        resolve(error.detail);
                    };
                    fileReader.onerror = reject
                    fileReader.readAsText(data);
                });
            } 
            console.error(exc);
            return;
        }
    }

    static async deleteMediaFile(mediaId) {
        try {
            const params = { mediaId: mediaId }
            const response = await api.delete('delete', { params });
            return response.data
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                const detail = exc.response.data.detail;
                if (typeof detail === 'string') {
                    error_message = detail;
                }
                else {
                    error_message = detail[0].msg;
                }
            } else {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

    static async retryDownload(mediaId) {
        try {
            const response = await api.put('retry', null, { params: { mediaId } });
            return response.data
        } catch (exc) {
            let error_message = null;
            if (exc.code === 'ERR_NETWORK'){
                error_message = "Network error or server is offline!"
            }
            else if (exc.response) {
                const detail = exc.response.data.detail;
                if (typeof detail === 'string') {
                    error_message = detail;
                }
                else {
                    error_message = detail[0].msg;
                }
            } else {
                console.error(exc);
                return;
            }
            throw Error(error_message);
        }
    }

}