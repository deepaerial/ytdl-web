import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';


const PreviewBox = styled.div`
    position: relative;
    background-size: cover;
    background-color: #FFF;
    border-radius: 0.4rem;
    min-width: 350px;
    max-width: auto;
    height: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    font-size: 0.9em;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
`;

const Preview = ({ preview, isDesktop }) => {
    if (preview) return;
    return (
        <PreviewBox>

        </PreviewBox>
    )
}

Preview.propTypes = {
    preview: PropTypes.shape({
        url: PropTypes.string,
        title: PropTypes.string,
        duration: PropTypes.number,
        thumbnailUrl: PropTypes.string,
        audioStreams: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.string.isRequired,
            mimetype: PropTypes.string.isRequired,
            bitrate: PropTypes.string.isRequired
        })),
        videoStreams: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.string.isRequired,
            mimetype: PropTypes.string.isRequired,
            resolution: PropTypes.string.isRequired
        })),
        mediaFormats: PropTypes.arrayOf(PropTypes.string)
    }),
    isDesktop: PropTypes.bool.isRequired
}

export default Preview;
