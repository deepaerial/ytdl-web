import React, { useContext, useEffect, useReducer, useState } from 'react';

import { Grid, Stack } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import { Slide } from 'react-toastify';

import Header from './components/Header.jsx'
import SearchBar from './components/SearchBar.jsx';

import { toast } from 'react-toastify';
import API from './api.js';
import { parametrizeUrl } from './utils.js';
import { LoadingContext } from './context/LoadingContext.jsx';
import { downloadsReducer } from './reducers.js'
import Preview from "./components/Preview.jsx"
import 'react-toastify/dist/ReactToastify.css';
import MediaItem from './components/MediaItem.jsx';
import { ACTION } from './constants.js';



const App = () => {
    const checkIsDesktop = () => {
        const viewportWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        return viewportWidth > 1024;
    };

    const [isDesktop, setIsDesktop] = useState(checkIsDesktop());
    const [version, setVersion] = useState("");
    const setIsLoading = useContext(LoadingContext);
    const [downloads, dispatch] = useReducer(downloadsReducer, {});
    const [preview, setPreview] = useState();

    const onProgressUpdate = (download) => {
        const { mediaId, status, progress } = download;
        dispatch({
            type: ACTION.STATUS_UPDATE,
            mediaId,
            status,
            progress
        });
    };

    const onDownloadsFetched = (downloads) => {
        setPreview(null);
        dispatch({
            type: ACTION.FETCH_ALL,
            downloads
        });
    };

    const onDownloadDelete = (download) => {
        const { mediaId, status, isAudio, title } = download;
        dispatch({
            type: ACTION.DELETE,
            mediaId,
            status
        });
        toast.success(`${isAudio ? "Audio" : "Video"} file \"${title}\" was successfully deleted.`)
    };

    useEffect(() => {
        const onAppStart = async () => {
            window.addEventListener('resize', () => setIsDesktop(checkIsDesktop()));
            const { apiVersion } = await API.getApiVersion();
            setVersion(apiVersion);
            const eventSource = new EventSource(parametrizeUrl(`${API_URL}/download/stream`), { withCredentials: true });
            eventSource.addEventListener("message", (event) => {
                onProgressUpdate(JSON.parse(event.data));
            });
            eventSource.addEventListener("end", (_) => {
                eventSource.close();
            });
            setIsLoading(false);
        };
        onAppStart();
    }, []);
    useEffect(() => {
        const donwloadListLoad = async () => {
            setIsLoading(true);
            const downloads = await API.getDownloads();
            onDownloadsFetched(downloads);
            setIsLoading(false);
        };
        donwloadListLoad();
    }, [version]);

    const renderDownloads = () => {
        if (isDesktop) {
            return (<Grid container spacing={3} justifyContent="center">
                {downloads && Object.entries(downloads).map(entry => {
                    const [key, download] = entry;
                    return <Grid item xs={3} key={key}>
                        <MediaItem downloadItem={download} onDeleteAction={onDownloadDelete} />
                    </Grid>
                })}
            </Grid>);
        }
        return (<Stack direction="column" justifyContent="center" alignItems="flex-start" spacing={2}>
            {downloads && Object.entries(downloads).map(entry => {
                const [key, download] = entry;
                return (<MediaItem key={key} downloadItem={download} onDeleteAction={onDownloadDelete} />);
            })
            }
        </Stack >);
    };
    return (
        <React.Fragment>
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
            <SearchBar isDesktop={isDesktop} setPreview={setPreview} />
            {preview && <Preview preview={preview} onDonwloadEnqueue={onDownloadsFetched} setPreview={setPreview} />}
            {renderDownloads()}
        </React.Fragment>
    );
}

export default App;
