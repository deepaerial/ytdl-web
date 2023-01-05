import React, { useContext, useState } from 'react'
import PropTypes from "prop-types";

import styled from 'styled-components';
import { LoadingContext } from '../context/LoadingContext.js';
import SearchIcon from '@mui/icons-material/Search';
import { toast } from 'react-toastify';
import API from '../api';

const SearchBarWrapper = styled.div`
    margin-top: 3rem;
    min-width: ${props => props.isDesktop ? 60 : 90}%;
    display: flex;
    align-items: center;
    padding: 0.5em 0.7em;
    border-radius: 2.9rem;
    background-color: #fff;
    border: none;
    transition: box-shadow 300;
    appearance: none;
    box-shadow: 0.2rem 0.2rem 0.9rem #000000;
`;

const SearchBarInput = styled.input`
    margin-left: 10px;
    width: 100%;
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
    width: 100px;
    height: 40px;
    font-size: 1rem;
    appearance: none;
    border: none;
    outline: none;
    background: linear-gradient(to right, #b8cbb8 0%, #b8cbb8 0%, #b465da 0%, #cf6cc9 33%, #ee609c 66%, #ee609c 100%);
    border-radius: 20px;
    color: #ffffff;
    box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);

    :hover{
        box-shadow: 0 3px 6px rgba(0,0,0,0.5), 0 3px 6px rgba(0,0,0,0.5);
    }
    :active{
        box-shadow: 3px 2px 22px 1px rgba(0, 0, 0, 0.24); 
    }
`


const SearchBar = ({ isDesktop, setPreview }) => {

    const [url, setUrl] = useState("");
    const setIsLoading = useContext(LoadingContext);

    const onSearch = async (event) => {
        event.preventDefault();
        try {
            setIsLoading(true);
            const preview = await API.getPreview(url);
            setPreview(preview);
        } catch (error) {
            console.error(error);
            toast.error(error.message)
        } finally {
            setIsLoading(false);
        }
    };

    const onChange = (event) => {
        const value = event.target.value;
        setUrl(value)
    };

    return (
        <SearchBarWrapper isDesktop={isDesktop}>
            <SearchIcon />
            <SearchBarInput name='search' type="text" placeholder="https://www.youtube.com/watch?v=..." value={url} onChange={onChange} />
            <SearchBarButton onClick={onSearch}>Search</SearchBarButton>
        </SearchBarWrapper>
    );
}

SearchBar.propTypes = {
    isDesktop: PropTypes.bool,
    setPreview: PropTypes.func
}
export default SearchBar;