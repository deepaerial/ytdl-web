import React from 'react';

import styled from 'styled-components';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch } from '@fortawesome/free-solid-svg-icons'

import Header from './Header.jsx'
import SearchBar from './SearchBar.jsx';

import { apiVersion, apiCheck } from '../api'
import DownloadsContext from '../context/DownloadsContext.jsx';

import "../styles.css"

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
        media_options: [],
    }

    async componentDidMount() {
        const success = await apiCheck();
        const {api_version, media_options} = await apiVersion();
        this.setState({ version: api_version , media_options});
    }


    render() {
        const {version, media_options} = this.state
        return (
            <Content>
                <Header version={version} />
                <DownloadsContext.Provider value={[]}>
                    <SearchBar mediaOptions={media_options}/>
                </DownloadsContext.Provider>
            </Content>
        )
    }
}

library.add(faSearch);

export default App;
