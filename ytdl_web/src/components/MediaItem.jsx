import React, { Component } from 'react'
import PropTypes from "prop-types";

import styled from 'styled-components';

import {bytesToHumanReadableFileSize, millisecToHumanReadable} from '../utils';


const CardBox = styled.div`
    position: relative;
    margin: ${props => props.isDesktop ? 20 : 20}px ${props => props.isDesktop ? 20 : 0}px;
    background-image: url(${props => props.backgroundUrl});
    background-size: cover;
    background-color: #FFF;
    border-radius: 0.4rem;
    max-width: 350px;
    height: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    font-size: 1.2em;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);

    :hover{
        box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
    }
`;

const Title = styled.div`
    margin-top: 10px;
    text-align: center;
`;

const Url = styled.a`
    text-decoration: none;
    color: #FFF;
    text-shadow: 2px 2px 3px #000;
    margin-top: 10px;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);

    :hover {
        text-shadow: 2px 2px 5px #fff;
    }
`;

const Duration = styled.span`
    position: absolute;
    color: #FFF;
    text-shadow: 2px 2px 3px #000;
    left: 5px;
    bottom: 10px;
`;

const Size = styled.span`
    position: absolute;
    color: #FFF;
    text-shadow: 2px 2px 3px #000;
    flex-grow: 1;
    right: 5px;
    bottom: 10px;
`;


export default class MediaItem extends Component {
    static propTypes = {
        downloadItem: PropTypes.object
    }

    render() {
        const { downloadItem, isDesktop } = this.props;
        const { title, thumbnail, video_url, duration, filesize } = downloadItem;
        return (
            <CardBox isDesktop={isDesktop} backgroundUrl={thumbnail.url}>
                <Title><Url href={video_url}>{title}</Url></Title>
                <Duration>{millisecToHumanReadable(duration)}</Duration>
                <Size>{bytesToHumanReadableFileSize(filesize)}</Size>
            </CardBox>
        )
    }
}
