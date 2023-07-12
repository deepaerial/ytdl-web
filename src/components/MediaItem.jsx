import React, { useContext } from 'react'
import PropTypes from "prop-types";

import styled from 'styled-components';

import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import { secondsToHumanReadable } from '../utils';
import { Statuses } from '../constants.js';

import DownloadSpinner from "./DownloadSpinner.jsx";
import {API} from '../api';
import { toast } from 'react-toastify';
import { LoadingContext } from '../context/LoadingContext.jsx';
import { IconButton } from '@mui/material';
import HighlightOffRoundedIcon from '@mui/icons-material/HighlightOffRounded';

import { useConfirm } from "material-ui-confirm";

import { styled as styledMui} from '@mui/system';

const CardBox = styled.div`
    position: relative;
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
    bottom: 15px;
`;

const ButtonsBox = styled.div`
    position: absolute;
    display: flex;
    justify-content: flex-end;
    flex-grow: 1;
    right: 5px;
    bottom: 10px;
`;

const HighlightOffRoundedIconCustomStyled = styledMui(HighlightOffRoundedIcon)(() => ({
    position: "absolute",
    left: "2.2em",
    top: "1.2em",
    color: "#de3e40",
    fontSize: "4rem"
}));


const MediaItem = ({ downloadItem, onDeleteAction }) => {

    const setIsLoading = useContext(LoadingContext);
    const confirm = useConfirm();
    const { mediaId, title, thumbnailUrl, url, duration, progress, status } = downloadItem;

    if (status === Statuses.FAILED){
        toast.error(`${title} failed to download.`)
    }

    const downloadMedia = async () => {
        setIsLoading(true);
        API.downloadMediaFile(mediaId).catch(e => toast.error(e.message)).finally(() => setIsLoading(false));
    }

    const onDeleteClick = async () => {
        confirm({description: "Are you sure you want to delete this download?"}).then(async () => await deleteMedia())
    }

    const deleteMedia = async () => {
        try {
            setIsLoading(true);
            const response = await API.deleteMediaFile(mediaId);
            onDeleteAction(response);
        } catch (error) {
            toast.error(error.message)
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <CardBox backgroundUrl={thumbnailUrl}>
            <Title><Url href={url} target="_blank" rel="noopener noreferrer">{title}</Url></Title>
            {
                [Statuses.DOWNLOADING, Statuses.CONVERTING].includes(status) && <DownloadSpinner progress={progress} />
            }
            {Statuses.FAILED === status && <HighlightOffRoundedIconCustomStyled />}
            <Duration>{secondsToHumanReadable(duration)}</Duration>
            <ButtonsBox>
                {[Statuses.FINISHED, Statuses.DOWNLOADED].includes(status) && <IconButton onClick={downloadMedia}><DownloadIcon sx={{ color: "#FFFFFF" }} /></IconButton>}
                {[Statuses.FINISHED, Statuses.DOWNLOADED, Statuses.FAILED].includes(status) && <IconButton onClick={onDeleteClick}><DeleteIcon sx={{ color: "#FFFFFF" }} /></IconButton>}
            </ButtonsBox>
        </CardBox >
    )
}

MediaItem.propTypes = {
    downloadItem: PropTypes.object,
    onDeleteAction: PropTypes.func
}

export default MediaItem;