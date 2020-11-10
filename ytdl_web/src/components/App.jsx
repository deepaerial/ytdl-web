import React from 'react';

import styled from 'styled-components';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch } from '@fortawesome/free-solid-svg-icons'

import Header from './Header.jsx'
import SearchBar from './SearchBar.jsx';

import { apiVersion, apiCheck } from '../api'
import DownloadsContext from '../context/DownloadsContext';

import "../styles.css"
import PendingList from './PendingList.jsx';

const Content = styled.div`
    display: flex;
	flex-direction: column;
	flex-wrap: nowrap;
	justify-content: center;
	align-items: center;
    align-content: center;
`;

class App extends React.Component {

    state = {
        version: null,
        downloads: [],
        mediaOptions: [],
        isDesktop: false
    }

    setIsDektop = () => {
        const viewportWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        this.setState({ isDesktop: viewportWidth >= 1024 });
    }


    async componentDidMount() {
        this.setIsDektop();
        window.addEventListener('resize', this.setIsDektop);
        const success = await apiCheck();
        const {api_version, media_options} = await apiVersion();
        this.setState({ version: api_version , mediaOptions: media_options});
    }

    setDownloads = (downloads) => {
        this.setState({downloads});
    }

    render() {
        const {version, downloads, mediaOptions, isDesktop} = this.state
        const {setDownloads} = this;
        return (
            <Content>
                <Header version={version} />
                <DownloadsContext.Provider value={{downloads, setDownloads}}>
                    <SearchBar mediaOptions={mediaOptions} isDesktop={isDesktop}/>
                    <PendingList isDesktop={isDesktop}/>
                </DownloadsContext.Provider>
            </Content>
        )
    }
}

library.add(faSearch);

export default App;
