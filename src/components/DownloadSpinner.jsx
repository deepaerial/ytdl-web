import * as React from 'react';
import PropTypes from 'prop-types';
import CircularProgress from '@mui/material/CircularProgress';
import { styled } from '@mui/system';

const CustomCircularProgress = styled(CircularProgress)(() => ({
    position: "absolute",
    left: "9.5em",
    top: "4.0em",
    color: "#b465da"
}));

const DownloadSpinner = ({ progress }) => {
    const options = {
        size: "80px"
    }
    if (progress >= 0) {
        Object.assign(options, {
            variant: "determinate",
            value: progress
        });
    }
    return <CustomCircularProgress {...options} />;
};

DownloadSpinner.propTypes = {
    progress: PropTypes.number
}


export default DownloadSpinner;