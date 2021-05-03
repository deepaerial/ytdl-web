import React, { Component } from 'react';
import PropTypes from "prop-types";

import styled, { keyframes } from 'styled-components';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import API from '../api';

const ripple = keyframes`
    to {
        transform: scale(4);
        opacity: 0;
    }
`;

const DownloadButtonWrapper = styled.button`
    position: absolute;
    appearance: none;
    border: none;
    outline: none;
    background: none;
    overflow: hidden;
    cursor: pointer;
    width: 100px;
    height: 100px;
    font-size: 30px;
    color: #ffffff;
    border-radius: 50%;
    padding: 10px;
    border: 1px solid #ffffff;
    text-align: center;
    left: 4.3em;
    top: 1.9em;

    :hover {
        box-shadow: 0 0 10px #ffffff;
    }
    :hover svg{
        filter: drop-shadow( 2px 2px 5px #ffffff);
    }

    svg {
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }

    span.ripple {
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: ${ripple} 600ms linear;
        background-color: rgba(255, 255, 255, 0.7);
    }
`;

export default class DownloadButton extends Component {

    static propTypes = {
        mediaId: PropTypes.string
    }

    makeRippleEffect = (event) => {
        const button = event.currentTarget;
        const spanElement = document.createElement("span");
        const pos = button.getBoundingClientRect();
        const size = button.offsetWidth;
        spanElement.style.width = spanElement.style.height = `${button.offsetWidth}px`;
        spanElement.style.left = `${event.clientX - pos.x - size/2}px`;
        spanElement.style.top = `${event.clientY-pos.y-size/2}px`;
        spanElement.classList.add("ripple"); 
        const ripple = button.getElementsByClassName("ripple")[0];
        if (ripple) {
            ripple.remove();
        }
        button.appendChild(spanElement);
    }

    downloadMedia = (mediaId) => {
        API.downloadMediaFile(mediaId);
    }

    render() {
        const {mediaId} = this.props;
        return (
            <DownloadButtonWrapper onClick={(event) => {
                this.makeRippleEffect(event);
                this.downloadMedia(mediaId);
            }}>
                <FontAwesomeIcon icon="download"></FontAwesomeIcon>
            </DownloadButtonWrapper>
        )
    }
}
