import React, { Component } from 'react'
import PropTypes from "prop-types";

import styled from 'styled-components';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

import IconButton from './IconButton.jsx';
import { millisecToHumanReadable, wrapFunc } from '../utils';
import { Statuses } from '../constants.js';

import API from '../api';
import { toast } from 'react-toastify';
import LoadingContext from '../context/LoadingContext';

const CardBox = styled.div`
    position: relative;
    margin: ${props => props.isDesktop ? 20 : 10}px ${props => props.isDesktop ? 20 : 5}px;
    background-image: linear-gradient(
          rgba(0, 0, 0, 0.3), 
          rgba(0, 0, 0, 0.5)
        ), url(${props => props.backgroundUrl});
    background-size: cover;
    background-color: #FFF;
    border-radius: 0.4rem;
    min-width: 350px;
    max-width: 350px;
    height: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    font-size: 0.9em;
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

const ButtonsBox = styled.div`
    position: absolute;
    width: 50px;
    display: flex;
    justify-content: space-between;
    flex-grow: 1;
    right: 5px;
    bottom: 10px;
    margin: 5px;
    margin-bottom: 1px;
`;

const LoaderContainer = styled.div`
    position: absolute;
    width: 100px;
    height: 100px;
    left: 8.9em;
    top: 3.9em;
`;
export default class MediaItem extends Component {

    static contextType = LoadingContext;

    static propTypes = {
        downloadItem: PropTypes.object,
        isDesktop: PropTypes.bool,
        downloadsContext: PropTypes.object
    }

    downloadMedia = async (mediaId) => {
        const { setIsLoading } = this.context;
        setIsLoading(true);
        API.downloadMediaFile(mediaId).catch(e => toast.error(e.message)).finally(() => setIsLoading(false));
    }

    deleteMedia = async (mediaId) => {
        const { downloadsContext } = this.props;
        const { downloads, setDownloads } = downloadsContext;
        const { setIsLoading } = this.context;
        try {
            setIsLoading(true);
            const {media_id, status} = await API.deleteMediaFile(mediaId);
            if (status === Statuses.DELETED) {
                delete downloads[media_id];
            }
            setDownloads(downloads);
        } catch (error) {
            toast.error(error.message)
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }

    render() {
        const { downloadItem, isDesktop, downloadsContext } = this.props;
        const { media_id, title, thumbnail, video_url, duration, progress, status } = downloadItem;
        const { downloadMedia, deleteMedia } = this;
        return (
            <CardBox isDesktop={isDesktop} backgroundUrl={thumbnail.url}>
                <Title><Url href={video_url} target="_blank" rel="noopener noreferrer">{title}</Url></Title>
                {
                    status === 'downloading' && <LoaderContainer>
                        <CircularProgressbar value={progress} text={`${progress}%`} styles={buildStyles({
                            textColor: "#FFFFFF",
                            trailColor: "rgb(214, 214, 214, 0.6)",
                            pathColor: "#7953d2",
                        })} />
                    </LoaderContainer>
                }
                <Duration>{millisecToHumanReadable(duration)}</Duration>
                <ButtonsBox>
                    {[Statuses.FINISHED, Statuses.DOWNLOADED].includes(status) && <IconButton size={15} colorOnHover={"#00FF7F"} icon="download" onClick={wrapFunc(downloadMedia, media_id)}/>}
                    {[Statuses.FINISHED, Statuses.DOWNLOADED].includes(status) && <IconButton size={15} colorOnHover={"#FF7377"} icon="trash-alt" onClick={wrapFunc(deleteMedia, media_id)}/>}
                </ButtonsBox>
            </CardBox>
        )
    }
}
