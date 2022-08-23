import React, { useEffect, useState } from 'react';

import styled from 'styled-components';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch, faDownload, faTrashAlt } from '@fortawesome/free-solid-svg-icons'
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

const App = () => {
    const checkIsDesktop = () => {
        const viewportWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        return viewportWidth > 1024;
    };
    const [isDesktop, setIsDesktop] = useState(checkIsDesktop());
    const [version, setVersion] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [downloads, setDownloads] = useState({});
    const [preview, setPreview] = useState(null);
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
                eventSource.addEventListener("end", (event) => {
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
                    {/* {preview && <Preview preview={preview} isDesktop={isDesktop} />} */}
                </DownloadsContext.Provider>
            </LoadingContext.Provider>
        </Content >
    );
}

library.add(faSearch, faDownload, faTrashAlt);

export default App;
