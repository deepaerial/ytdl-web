import React, { useState } from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Button from '@mui/material/Button';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import Typography from '@mui/material/Typography';


const PreviewBox = styled.div`
    position: relative;
    display: flex;
    padding: 10px;
    background-size: cover;
    background-color: #FFF;
    min-width: 50%;
    max-height: 250px;
    border-radius: 0.4rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
`;

const Thumbnail = styled.div`
  position: relative;
  background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.5)), url("https://i.ytimg.com/vi/AWkqqGFyebY/hqdefault.jpg");
  background-size: cover;
  background-color: #fff;
  border-radius: 0.4rem;
  height: 200px;
  width: 300px;
  `;

const Preview = ({ preview, isDesktop }) => {
    const [audioStream, setAudioStream] = useState(preview.audioStreams[0].id)
    const [videoStream, setVideoStream] = useState(preview.videoStreams[0].id)
    const [mediaFormat, setMediaFormat] = useState(preview.mediaFormats[0])

    const { audioStreams, videoStreams, mediaFormats } = preview;

    return (
        <Card sx={{ maxWidth: 300 }}>
            <CardMedia
                component="img"
                alt="green iguana"
                height="180"
                image={preview.thumbnailUrl}
            />
            <CardContent>
                <Typography gutterBottom variant="p" fontWeight="bold" component="div">
                    {preview.title}
                </Typography>
                <FormControl sx={{ m: 1, width: 200 }}>
                    <InputLabel id="audio-bitrate-select-label">Audio bitrate</InputLabel>
                    <Select
                        labelId="audio-sbitrate-select-label"
                        id="audio-bitrate-select"
                        value={audioStream}
                        label="Audio bitrate"
                        onChange={(e) => setAudioStream(e.target.value)}
                    >
                        {audioStreams.map((a) =>
                            <MenuItem key={a.id} value={a.id}>{a.bitrate} {a.mimetype}</MenuItem>
                        )}
                    </Select>
                </FormControl>
                <FormControl sx={{ m: 1, width: 200 }}>
                    <InputLabel id="video-stream-select-label">Video stream</InputLabel>
                    <Select
                        labelId="video-stream-select-label"
                        id="video-stream-select"
                        value={videoStream}
                        label="Video stream"
                        onChange={(e) => setVideoStream(e.target.value)}
                    >
                        {videoStreams.map((v) =>
                            <MenuItem key={v.id} value={v.id}>{v.resolution} {v.mimetype}</MenuItem>
                        )}
                    </Select>
                </FormControl>
                <FormControl sx={{ m: 1, width: 200 }}>
                    <InputLabel id="media-format-select-label">Media format</InputLabel>
                    <Select
                        labelId="media-format-select-label"
                        id="media-format-select"
                        value={mediaFormat}
                        label="Media format"
                        onChange={(e) => setMediaFormat(e.target.value)}
                    >
                        {mediaFormats.map((m) =>
                            <MenuItem key={m} value={m}>{m}</MenuItem>
                        )}
                    </Select>
                </FormControl>
            </CardContent>
            <CardActions>
                <Button variant="contained" startIcon={<FileDownloadIcon />}>
                    Download
                </Button>
            </CardActions>
        </Card>
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
