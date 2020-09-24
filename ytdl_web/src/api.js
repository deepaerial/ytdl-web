const API_URL = 'https://127.0.0.1:8000/api'


export const fetchVersion = async () => {
    const response = await fetch(`${API_URL}/version`, {credentials: 'include'});
    const data = await response.json();
    return data.api_version;
};

export const sessionCheck = async () => {
    const response = await fetch(`${API_URL}/check`, {credentials: 'include'});
    const status = response.status;
    return status;
};

// export const 