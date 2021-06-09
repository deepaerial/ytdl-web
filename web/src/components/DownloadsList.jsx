import React, { Component } from 'react';
import PropTypes from "prop-types";
import DownloadsContext from '../context/DownloadsContext';
import styled from 'styled-components';

import MediaItem from './MediaItem.jsx';

const ListContainer = styled.div`
    max-width: ${props => props.isDesktop ? 60 : 90}%;
    margin-top: 15px;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-content: space-around;
    justify-content: ${props => props.isDesktop ? "space-around" : "center"};
`;
export default class DownloadsList extends Component {

    static contextType = DownloadsContext;

    static propTypes = {
        isDesktop: PropTypes.bool
    }

    render() {
        const { downloads } = this.context;
        const { isDesktop } = this.props;
        return (
            <ListContainer isDesktop={isDesktop}>
                {Object.entries(downloads).map(([k, v]) => v).map((download, index) => <MediaItem key={index} downloadItem={download} downloadsContext={this.context}/>)}
            </ListContainer>
        )
    }
}
