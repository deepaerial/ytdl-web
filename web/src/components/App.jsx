import React, { useEffect, useState } from 'react';

import styled from 'styled-components';
import { toast, ToastContainer } from 'react-toastify';
import { Slide } from 'react-toastify';

import Header from './Header.jsx'
import SearchBar from './SearchBar.jsx';

import API from '../api';
import { parametrizeUrl } from '../utils';
import DownloadsContext from '../context/DownloadsContext';
import LoadingContext from '../context/LoadingContext.js';
import Loader from './Loader.jsx';

import "../../public/styles.css";
import 'react-toastify/dist/ReactToastify.css';
import Preview from './Preview.jsx';


const Content = styled.div`
    display: flex;
	flex-direction: column;
	flex-wrap: nowrap;
	justify-content: center;
	align-items: center;
    align-content: center;
`;

const LoaderContainer = styled.div`
    width: ${props => props.size}px;
    height: ${props => props.size}px;
    position: fixed;
    top: 1rem;
    z-index: 1000;
    box-shadow: 0.2rem 0.2rem 0.9rem #000000;
    border-radius: 50%;
    background-color: #ffffff;
`;

const FIXTURE = {
    "url": "https://www.youtube.com/watch?v=dCCYALKSZEs",
    "title": "This is a good intermediate react interview challenge",
    "duration": 2309,
    "thumbnailUrl": "https://i.ytimg.com/vi/dCCYALKSZEs/sddefault.jpg?sqp=-oaymwEmCIAFEOAD8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGGUgZShlMA8=&rs=AOn4CLA0qWOH8BgIp9bRX5vYnOxDuSB6oQ",
    "audioStreams": [
        {
            "id": "251",
            "mimetype": "audio/webm",
            "bitrate": "160kbps"
        },
        {
            "id": "250",
            "mimetype": "audio/webm",
            "bitrate": "70kbps"
        },
        {
            "id": "249",
            "mimetype": "audio/webm",
            "bitrate": "50kbps"
        },
        {
            "id": "140",
            "mimetype": "audio/mp4",
            "bitrate": "128kbps"
        },
        {
            "id": "139",
            "mimetype": "audio/mp4",
            "bitrate": "48kbps"
        }
    ],
    "videoStreams": [
        {
            "id": "278",
            "mimetype": "video/webm",
            "resolution": "144p"
        },
        {
            "id": "242",
            "mimetype": "video/webm",
            "resolution": "240p"
        },
        {
            "id": "243",
            "mimetype": "video/webm",
            "resolution": "360p"
        },
        {
            "id": "244",
            "mimetype": "video/webm",
            "resolution": "480p"
        },
        {
            "id": "247",
            "mimetype": "video/webm",
            "resolution": "720p"
        },
        {
            "id": "248",
            "mimetype": "video/webm",
            "resolution": "1080p"
        }
    ],
    "mediaFormats": [
        "mp4",
        "mp3",
        "wav"
    ]
}

const App = () => {
    const checkIsDesktop = () => {
        const viewportWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        return viewportWidth > 1024;
    };
    const [isDesktop, setIsDesktop] = useState(checkIsDesktop());
    const [version, setVersion] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [downloads, setDownloads] = useState({});
    const [preview, setPreview] = useState(FIXTURE);
    const loaderSize = 50;

    const onProgressUpdate = (download) => {
        const { media_id, status, progress } = download;
        let downloadItem = downloads[media_id];
        if (downloadItem) {
            downloadItem = Object.assign(downloadItem, {
                status, progress
            });
            downloads[media_id] = downloadItem;
            setDownloads(prevDownloads => {
                return { ...prevDownloads, ...downloads }
            });
        }
    };
    useEffect(() => {
        const onAppStart = async () => {
            window.addEventListener('resize', () => setIsDesktop(checkIsDesktop()));
            try {
                const { apiVersion } = await API.getApiVersion();
                setVersion(apiVersion);
                const eventSource = new EventSource(parametrizeUrl(`${API_URL}/download/stream`), { withCredentials: true });
                eventSource.addEventListener("message", (event) => {
                    onProgressUpdate(JSON.parse(event.data));
                });
                eventSource.addEventListener("end", (_) => {
                    eventSource.close();
                });
            } catch (error) {
                toast.error(error.message);
                throw error;
            } finally {
                setIsLoading(false);
            }
        };
        onAppStart();
    }, []);
    return (
        <Content>
            <ToastContainer
                position={isDesktop ? "top-right" : "top-center"}
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={true}
                transition={Slide}
                draggable
                pauseOnHover
            />
            {isLoading && <LoaderContainer size={loaderSize}><Loader heightAndWidth={loaderSize} /> </LoaderContainer>}
            <Header version={version} />
            <LoadingContext.Provider value={isLoading}>
                <DownloadsContext.Provider value={downloads}>
                    <SearchBar isDesktop={isDesktop} />
                    {preview && <Preview preview={preview} isDesktop={isDesktop} />}
                </DownloadsContext.Provider>
            </LoadingContext.Provider>
        </Content >
    );
}

export default App;
