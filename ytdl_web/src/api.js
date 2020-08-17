const API_URL = 'http://127.0.0.1:8000/api/'


export const fetchVersion = async () => {
    const response = await fetch(API_URL+'version');
    const data = await response.json();
    return data.api_version;
};

// export const 