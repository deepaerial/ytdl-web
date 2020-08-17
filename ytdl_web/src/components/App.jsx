import React from 'react';

import styled from 'styled-components';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch } from '@fortawesome/free-solid-svg-icons'

import Header from './Header.jsx'
import SearchBar from './SearchBar.jsx';

import { fetchVersion } from '../api.js'

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
        version: null
    }

    async componentDidMount() {
        const version = await fetchVersion();
        this.setState({ version });
    }

    onSearch = async (event) => {
        event.preventDefault();
        alert(this.state.version);
    };

    render() {
        return (
            <Content>
                <Header version={this.state.version} />
                <SearchBar onSearch={this.onSearch} />
            </Content>
        )
    }
}

library.add(faSearch);

export default App;
