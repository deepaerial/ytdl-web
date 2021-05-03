import { getFilenameFromContentDisposition } from './utils'
import axios from 'axios';
import { UID_KEY } from './constants';

const api = axios.create({ baseURL: API_URL });

class API {

    static async getClientInfo(errorCallback = null) {
        try {
            const uid = localStorage.getItem(UID_KEY);
            const response = await api.get('info', { params: uid ? { uid } : {} });
            localStorage.setItem(UID_KEY, response.data.uid);
            return response.data;
        } catch (exc) {
            if (errorCallback) {
                errorCallback(exc);
                return;
            }
            if (exc.response) {
                alert(exc.response.data.detail);
            } else {
                alert(exc.message)
            }
            return {};
        }
    }

    static async fetchMediaInfo(videoUrl, mediaFormat, errorCallback = null) {
        try {
            const uid = localStorage.getItem(UID_KEY);
            const response = await api.put('fetch', {
                url: videoUrl,
                media_format: mediaFormat
            }, { params: (uid) ? { uid } : {} });
            return response.data.downloads;
        } catch (exc) {
            if (errorCallback) {
                errorCallback(exc);
                return;
            }
            if (exc.response) {
                const detail = exc.response.data.detail;
                if (typeof detail === 'string') {
                    alert(detail);
                }
                else {
                    alert(detail[0].msg);
                }
            } else {
                alert(exc.message)
            }
            return [];
        }
    }

    static async downloadMediaFile(mediaId, errorCallback = null) {
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
            if (errorCallback) {
                errorCallback(exc);
                return;
            }
            const data = exc.response.data;
            const fileReader = new FileReader();
            fileReader.onload = (e) => {
                const data = JSON.parse(e.target.result);
                alert(data.detail);
            };
            fileReader.readAsText(data);
        }
    }

}

export default API;