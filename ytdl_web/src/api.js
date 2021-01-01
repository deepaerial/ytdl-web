import { getFilenameFromContentDisposition, parametrizeUrl } from './utils'

import { UID_KEY } from './constants'

export const API_URL = 'https://127.0.0.1:8000/api'


export const apiInfo = async () => {
    let url = `${API_URL}/info`;
    const uid = localStorage.getItem(UID_KEY);
    if (uid) {
        url = parametrizeUrl(url, { uid });
    }
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) {
        alert(`Error ${response.status}`);
    }
    const json_response = await response.json();
    localStorage.setItem(UID_KEY, json_response.uid);
    return json_response;
};

export const apiFetch = async (uid, videoUrl, media_format) => {
    let json_body = {
        url: videoUrl,
        media_format
    }
    const url = parametrizeUrl(`${API_URL}/fetch`, { uid });
    const response = await fetch(url, {
        method: 'PUT',
        body: JSON.stringify(json_body)
    });
    if (!response.ok) {
        throw Error(`Error ${response.status}`);
    }
    const data = await response.json();
    return data.downloads;
};

export const apiDownload = (uid, mediaId) => {
    const url = parametrizeUrl(`${API_URL}/fetch`, { uid, media_id: mediaId })
    var a = document.createElement('a');
    a.href = url;
    a.click();   
};