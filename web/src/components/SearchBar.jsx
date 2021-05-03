import React, { Component } from 'react'
import PropTypes from "prop-types";

import styled, { keyframes } from 'styled-components';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import DownloadsContext from '../context/DownloadsContext';

import API from '../api';

const SearchBarWrapper = styled.div`
    margin-top: 3rem;
    min-width: ${props => props.isDesktop ? 60 : 90}%;
    display: flex;
    align-items: flex-start;
    padding: 0.5rem;
    border-radius: 0.4rem;
    background-color: #fff;
    border: none;
    line-height: 1.0rem;
    transition: box-shadow 300;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    box-shadow: 0.2rem 0.2rem 0.9rem #000000;
`;

const SearchBarInput = styled.input`
    width: 100%;
    margin: auto 0;
    border: none;
    font-size: 1.2rem;

    ::placeholder {
        color: #B0BEC5; 
    }

    :focus {
        outline: none;
    }

    :-webkit-autofill {
        font-size: 1.2rem;
        box-shadow: 0 0 0px 1000px #fff inset;
    }
`;

const SearchBarMediaSelect = styled.select`
    appearance: none;
    border: none;
    background-color: #FFF;
    font-size: 1.2rem;
    line-height: 2.5rem;
    margin-right: 1rem;
`;

const SearchBarButton = styled.button`
    width: 40px;
    height: 40px;
    font-size: 1rem;
    appearance: none;
    border: none;
    outline: none;
    background: none;
    border-radius: 50%;
    box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);

    :hover{
        box-shadow: 0 3px 6px rgba(0,0,0,0.5), 0 3px 6px rgba(0,0,0,0.5);
    }
    :active{
        box-shadow: 3px 2px 22px 1px rgba(0, 0, 0, 0.24); 
    }
`


export default class SearchBar extends Component {

    static contextType = DownloadsContext;

    static propTypes = {
        mediaOptions: PropTypes.arrayOf(PropTypes.string),
        isDesktop: PropTypes.bool,
    }

    state = {
        url: '',
        isDesktop: false,
        selectedMediaOption: null,
    }

    componentDidUpdate = (prevProps) => {
        const { mediaOptions } = this.props;
        if (mediaOptions !== prevProps.mediaOptions) {
            if (mediaOptions) {
                this.setState({ selectedMediaOption: mediaOptions[0] });
            }
        }
    }

    onSearch = async (event) => {
        event.preventDefault();
        const downloads = await API.fetchMediaInfo(this.state.url, this.state.selectedMediaOption);
        if (downloads.length) {
            const { setDownloads } = this.context;
            setDownloads(downloads);
        }
        this.setState({ url: '' });
    };

    onChange = (event) => {
        const value = event.target.value;
        if (event.target.name === 'search') {
            this.setState({ url: value })
        } else {
            this.setState({ selectedMediaOption: value });
        }
    }


    render() {
        const { mediaOptions, isDesktop } = this.props;
        const { selectedMediaOption } = this.state;
        const selectProps = {
            name: mediaOptions,
            onChange: this.onChange
        }
        if (selectedMediaOption) {
            selectProps.value = selectedMediaOption;
        }
        return (
            <SearchBarWrapper isDesktop={isDesktop}>
                <SearchBarInput name='search' type="text" placeholder="Video URL..." value={this.state.url} onChange={this.onChange} />
                <SearchBarMediaSelect {...selectProps}>
                    {mediaOptions.map((option, index) => <option key={option} value={option}>{option}</option>)}
                </SearchBarMediaSelect>
                <SearchBarButton onClick={this.onSearch}><FontAwesomeIcon icon="search" /></SearchBarButton>
            </SearchBarWrapper>
        )
    }
}
