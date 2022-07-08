import React, { useEffect, useState } from 'react';

import styled from 'styled-components';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch, faDownload, faTrashAlt } from '@fortawesome/free-solid-svg-icons'
import { toast, ToastContainer } from 'react-toastify';
import { Slide } from 'react-toastify';

import Header from './Header.jsx'
import SearchBar from './SearchBar.jsx';

import API from '../api';
import { parametrizeUrl, mapDownloads } from '../utils';
import { DOWNLOADS } from '../constants';
import DownloadsContext from '../context/DownloadsContext';
import LoadingContext from '../context/LoadingContext.js';
import DownloadsList from './DownloadsList.jsx';
import Loader from './Loader.jsx';

import "../../public/styles.css";
import 'react-toastify/dist/ReactToastify.css';


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
    const { isDesktop, setIsDesktop } = useState(checkIsDesktop());
    const { isLoading, setIsLoading } = useState(false);
    const { downloads, setDownloads } = useState({});

    const onProgressUpdate = (download) => {
        const { media_id, status, progress } = download;
        let downloadItem = downloads[media_id];
        if (downloadItem) {
            downloadItem = Object.assign(downloadItem, {
                status, progress
            });
            downloads[media_id] = downloadItem;
            this.setDownloads(prevDownloads => {
                return { ...prevDownloads, ...downloads }
            });
        }
    };
    useEffect(() => {
        window.addEventListener('resize', () => setIsDesktop(checkIsDesktop()));
        try {
            setIsLoading(true);
            const { api_version, media_options, uid, downloads } = await API.getClientInfo();
            this.setState({ version: api_version, mediaOptions: media_options, downloads: mapDownloads(downloads) });
            if (uid) {
                const eventSource = new EventSource(parametrizeUrl(`${API_URL}/fetch/stream`, { uid }));
                eventSource.addEventListener("message", (event) => {
                    onProgressUpdate(JSON.parse(event.data));
                });
                eventSource.addEventListener("end", (event) => {
                    eventSource.close();
                });
            }
        } catch (error) {
            toast.error(error.message);
        } finally {
            this.setIsLoading(false);
        }
    });

    render() {
        const { version, mediaOptions, isDesktop, isLoading } = this.state;
        let downloads = this.state.downloads;
        const { setDownloads, setIsLoading } = this;
        if (!Object.keys(downloads).length) {
            downloads = localStorage.getItem(DOWNLOADS);
            if (downloads) downloads = JSON.parse(downloads);
            else downloads = {}
        }
        const loaderSize = 50;
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
                <LoadingContext.Provider value={{ isLoading, setIsLoading }}>
                    <DownloadsContext.Provider value={{ downloads, setDownloads }}>
                        <LoadingContext.Consumer>
                            {({ setIsLoading }) => <React.Fragment>
                                <DownloadsContext.Consumer>
                                    {({ setDownloads }) => <React.Fragment>
                                        <SearchBar mediaOptions={mediaOptions} isDesktop={isDesktop} setDownloads={setDownloads} setIsLoading={setIsLoading} />
                                        <DownloadsList isDesktop={isDesktop} />
                                    </React.Fragment>}
                                </DownloadsContext.Consumer>
                            </React.Fragment>}
                        </LoadingContext.Consumer>
                    </DownloadsContext.Provider>
                </LoadingContext.Provider>
            </Content>
        )
    }
}

library.add(faSearch, faDownload, faTrashAlt);

export default App;
