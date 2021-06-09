import React from 'react'
import PropTypes from "prop-types";

import styled, { keyframes } from 'styled-components';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

const minify = keyframes`
    to {
        transform: scale(0.75);
    }
`;

const ButtonWrapper = styled.button`
    appearance: none;
    border: none;
    outline: none;
    background: none;
    overflow: hidden;
    cursor: pointer;
    width: 20px;
    height: 20px;
    font-size: ${props => props.size}px;
    transition: all 0.3s cubic-bezier(.25, .8, .25, 1);

    :hover {
        transform: scale(1.23);
    }

    :hover svg{
        filter: brightness(1);
        color: ${props => props.colorOnHover};
    }

    :active svg{
        animation: ${minify} 300ms linear;
    }

    :visited {}

    svg {
        width: 20px;
        height: 20px;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        color: #ffffff;
    }
`;


export default function IconButton({ size, colorOnHover, icon, onClick }) {
    return (
        <ButtonWrapper onClick={async (event) => {
            const AsyncFunction = (async () => { }).constructor;
            if (onClick instanceof AsyncFunction) await onClick();
            else onClick();
        }} size={size} colorOnHover={colorOnHover}>
            <FontAwesomeIcon icon={icon} fixedWidth></FontAwesomeIcon>
        </ButtonWrapper>
    )
}

IconButton.propTypes = {
    size: PropTypes.number,
    colorOnHover: PropTypes.string,
    icon: PropTypes.string,
    onClick: PropTypes.func
}
