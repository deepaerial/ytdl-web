import React, {useState} from "react";
import PropTypes from "prop-types";
import { toast } from 'react-toastify';

import styled from 'styled-components';


const HeaderTitle = styled.div`
    margin-top: 50%;
    margin-left: 5px;
    display: flex;
    justify-content: center;
    background-image: linear-gradient(to right, #b8cbb8 0%, #b8cbb8 0%, #b465da 0%, #cf6cc9 33%, #ee609c 66%, #ee609c 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -moz-background-clip: text;
    -webkit-text-fill-color: transparent; 
    -moz-text-fill-color: transparent;
`;

const AppTitle = styled.h1`
    font-size: 3em;
    font-weight: 200;
`;

const Version = styled.span`
    display: block;
    margin-top: 2px;
    font-size: 0.9em;
`;

const Description = styled.p`
    margin-top: 10px;
`;

const Header = ({ version, apiVersion }) => {

    const [counter, setCounter] = useState(0)

    const onClickHeader = () => {
        if (counter === 3) {
            toast.info(`API version: ${apiVersion}`);
            setCounter(0)
        }
        else {
            setCounter(counter + 1);
        }
    }
    return (
        <header>
            <HeaderTitle onClick={onClickHeader}>
                <AppTitle>YTDL</AppTitle>
                {version && <Version>ver. {version}</Version>}
            </HeaderTitle>
            <Description>Web video downloader</Description>
        </header>
    )
}

Header.propTypes = {
    version: PropTypes.string.isRequired,
    apiVersion: PropTypes.string
}

export default Header;


