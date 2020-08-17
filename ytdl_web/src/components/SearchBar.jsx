import React, { Component } from 'react'
import PropTypes from "prop-types";

import styled, { keyframes } from 'styled-components'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const SearchBarWrapper = styled.form`
    margin-top: 3rem;
    width: 60%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 1.0rem 1.5rem 1.0rem 1.0rem;
    border-radius: 0.4rem;
    background-color: #fff;
    border: none;
    line-height: 0.3rem;
    transition: box-shadow 300;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    box-shadow: 0.2rem 0.2rem 0.9rem #000000;
`;
const SearchBarInput = styled.input`
    width: 95%;
    border: none;

    ::placeholder {
        color: #B0BEC5;
        font-size: 1rem;
    }

    :focus {
        outline: none;
    }
`;

const SearchBarButton = styled.button`
    font-size: 1rem;
    appearance: none;
    border: none;
    outline: none;
    background: none;
`


export default class SearchBar extends Component {
    static propTypes = {
        onSearch: PropTypes.func.isRequired,
    }
    render() {
        return (
            <SearchBarWrapper onSubmit={this.props.onSearch}>
                <SearchBarInput name='search' type="text" placeholder="Your text here..." />
                <SearchBarButton><FontAwesomeIcon icon="search" /></SearchBarButton>
            </SearchBarWrapper>
        )
    }
}
