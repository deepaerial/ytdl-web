import React, { useState } from 'react';

import styled from 'styled-components';

const LoaderContainer = styled.div`
    width: ${props => props.size}px;
    height: ${props => props.size}px;
    position: fixed;
    top: 1rem;
    z-index: 1000;
    box-shadow: 0.2rem 0.2rem 0.9rem #000000;
    border-radius: 50%;
    background-color: #ffffff;
`;

const LoaderSpinner = styled.svg`
  animation: rotate 1s linear infinite;
  width: ${props => props.size}px;
  height: ${props => props.size}px;

  & .path {
    stroke: #cf6cc9;
    stroke-linecap: round;
    animation: dash 1.5s ease-in-out infinite;
  }

  @keyframes rotate {
    100% {
      transform: rotate(360deg);
    }
  }
  @keyframes dash {
    0% {
      stroke-dasharray: 1, 150;
      stroke-dashoffset: 0;
    }
    50% {
      stroke-dasharray: 90, 150;
      stroke-dashoffset: -35;
    }
    100% {
      stroke-dasharray: 90, 150;
      stroke-dashoffset: -124;
    }
  }
`;

const Loader = ({ heightAndWidth }) => {
  return (
    <LoaderSpinner size={heightAndWidth || 50} viewBox="0 0 50 50" >
      <circle
        className="path"
        cx="25"
        cy="25"
        r="20"
        fill="none"
        strokeWidth="2"
      />
    </LoaderSpinner >
  )
};

const LoadingContext = React.createContext({
  setIsLoading: () => { }
});

const LoadingContextProvider = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);
  const loaderSize = 50;
  return (
    <LoadingContext.Provider value={setIsLoading}>
      {isLoading && <LoaderContainer size={loaderSize}><Loader heightAndWidth={loaderSize} /></LoaderContainer>}
      <LoadingContext.Consumer>
        {setIsLoading => (
          children
        )}
      </LoadingContext.Consumer>
    </LoadingContext.Provider>
  )
};

export { LoadingContext, LoadingContextProvider }
