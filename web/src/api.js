import { getFilenameFromContentDisposition } from './utils'
import axios from 'axios';
import { UID_KEY, Statuses } from './constants';

const api = axios.create({ baseURL: API_URL });

class API {

    static async getClientInfo() {
        try {
            const uid = localStorage.getItem(UID_KEY);
            const response = await api.get('client_info', { params: uid ? { uid } : {} });
            localStorage.setItem(UID_KEY, response.data.uid);
            return response.data;
        } catch (exc) {
            let error_message = null;
            if (exc.response) {
                error_message = exc.response.data.detail;
            } else {
                error_message = exc.message;
            }
            throw Error(error_message);
        }
    }

    static async fetchMediaInfo(videoUrl, mediaFormat) {
        try {
            const uid = localStorage.getItem(UID_KEY);
            const response = await api.put('fetch', {
                url: videoUrl,
                media_format: mediaFormat
            }, { params: (uid) ? { uid } : {} });
            return response.data.downloads;
        } catch (exc) {
            let error_message = null;
            if (exc.response) {
                const detail = exc.response.data.detail;
                if (typeof detail === 'string') {
                    error_message = detail;
                }
                else {
                    error_message = detail[0].msg;
                }
            } else {
                error_message = exc.message;
            }
            throw Error(error_message);
        }
    }

    static async downloadMediaFile(mediaId) {
        try {
            const uid = localStorage.getItem(UID_KEY);
            const params = { media_id: mediaId }
            if (uid) {
                params.uid = uid;
            }
            const response = await api.get('fetch', { params, responseType: 'blob' });
            const filename = getFilenameFromContentDisposition(response);
            const link = document.createElement('a');
            link.href = URL.createObjectURL(response.data);
            link.download = filename;
            link.click();
        } catch (exc) {
            let error_message = null;
            if (exc.response) {
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
            } else
                error_message = exc.message;
            throw Error(error_message);
        }
    }

    static async deleteMediaFile(mediaId) {
        try {
            const uid = localStorage.getItem(UID_KEY);
            const params = { media_id: mediaId }
            if (uid) {
                params.uid = uid;
            }
            const response = await api.delete('delete', { params });
            return response.data
        } catch (exc) {
            let error_message = null;
            if (exc.response) {
                const detail = exc.response.data.detail;
                if (typeof detail === 'string') {
                    error_message = detail;
                }
                else {
                    error_message = detail[0].msg;
                }
            } else {
                error_message = exc.message;
            }
            throw Error(error_message);
        }
    }

}

export default API;