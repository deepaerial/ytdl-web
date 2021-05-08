import React from 'react';

import styled from 'styled-components';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch, faDownload } from '@fortawesome/free-solid-svg-icons'
import { toast, ToastContainer } from 'react-toastify';
import { Slide } from 'react-toastify';

import Header from './Header.jsx'
import SearchBar from './SearchBar.jsx';

import API from '../api';
import { parametrizeUrl } from '../utils';
import { DOWNLOADS} from '../constants';
import DownloadsContext from '../context/DownloadsContext';
import DownloadsList from './DownloadsList.jsx';

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


const mapDownloads = (downloads) => {
    downloads = Object.assign({}, ...downloads.map(d => {
        const { media_id } = d;
        return { [media_id]: d }
    }));
    localStorage.setItem(DOWNLOADS, JSON.stringify(downloads));
    return downloads;
};

class App extends React.Component {

    state = {
        version: null,
        downloads: {},
        mediaOptions: [],
        isDesktop: false
    }

    setIsDektop = () => {
        const viewportWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        this.setState({ isDesktop: viewportWidth > 1024 });
    }


    async componentDidMount() {
        this.setIsDektop();
        window.addEventListener('resize', this.setIsDektop);
        try {
            const { api_version, media_options, uid, downloads } = await API.getClientInfo();
            this.setState({ version: api_version, mediaOptions: media_options, downloads: mapDownloads(downloads) });
            if (uid){
                const eventSource = new EventSource(parametrizeUrl(`${API_URL}/fetch/stream`, { uid }));
                eventSource.addEventListener("message", (event) => {
                    this.onProgressUpdate(JSON.parse(event.data));
                });
                eventSource.addEventListener("end", (event) => {
                    eventSource.close();
                });
            }
        } catch (error) {
            toast.error(error.message);
        }
    }

    setDownloads = (downloads) => {
        downloads = mapDownloads(downloads);
        this.setState({ downloads });
    }

    onProgressUpdate = (download) => {
        const { media_id, status, progress } = download;
        const { downloads } = this.state;
        let downloadItem = downloads[media_id];
        if (downloadItem) {
            downloadItem = Object.assign(downloadItem, {
                status, progress
            });
            downloads[media_id] = downloadItem;
            localStorage.setItem(DOWNLOADS, JSON.stringify(downloads));
            this.setState({ downloads });
        }
    }

    render() {
        const { version, mediaOptions, isDesktop } = this.state;
        let downloads = this.state.downloads;
        const { setDownloads } = this;
        if (!Object.keys(downloads).length) {
            downloads = localStorage.getItem(DOWNLOADS);
            if (downloads) downloads = JSON.parse(downloads);
            else downloads = {}
        }
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
                <Header version={version} />
                <DownloadsContext.Provider value={{ downloads, setDownloads }}>
                    <SearchBar mediaOptions={mediaOptions} isDesktop={isDesktop} />
                    <DownloadsList isDesktop={isDesktop} />
                </DownloadsContext.Provider>
            </Content>
        )
    }
}

library.add(faSearch, faDownload);

export default App;
