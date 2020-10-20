const API_URL = 'https://127.0.0.1:8000/api'


export const apiVersion = async () => {
    const response = await fetch(`${API_URL}/version`, { credentials: 'include' });
    if (!response.ok) {
        alert(`Error ${response.status}`);
    }
    return await response.json();
};

export const apiCheck = async () => {
    const response = await fetch(`${API_URL}/check`, { credentials: 'include' });
    if (!response.ok) {
        alert(`Error ${response.status}`);
    }
    const status = response.status;
    return status;
};

export const apiFetch = async (urls, media_format) => {
    let json_body = {
        urls,
        media_format
    }
    const response = await fetch(`${API_URL}/fetch`, {
        method: 'PUT',
        body: JSON.stringify(json_body)
    });
    if (!response.ok) {
        throw Error(`Error ${response.status}`);
    }
    const data = await response.json();
    return data.downloads;
}