import React from 'react';
import ReactDom from 'react-dom/client';
import styled from 'styled-components';

import App from './App.jsx';
import { LoadingContextProvider } from './context/LoadingContext.jsx';

import "./styles.css";

const Content = styled.div`
    display: flex;
	flex-direction: column;
	flex-wrap: nowrap;
	justify-content: center;
	align-items: center;
    align-content: center;
`;

const container = document.getElementById('app');
const root = ReactDom.createRoot(container);
root.render(
    <Content>
        <LoadingContextProvider>
            <App />
        </LoadingContextProvider>
    </Content>
);