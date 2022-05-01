import React, { Component } from 'react';
import PreviewContext from '../context/PreviewContext';


const PreviewBox = styled.div`
    position: relative;
    background-size: cover;
    background-color: #FFF;
    border-radius: 0.4rem;
    min-width: 350px;
    max-width: 350px;
    height: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    font-size: 0.9em;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
`;

export default class Preview extends Component {
    static contextType = PreviewContext;

    static propTypes = {
        downloadItem: PropTypes.object,
        isDesktop: PropTypes.bool,
        downloadsContext: PropTypes.object
    }

    render() {
        <PreviewBox>
            
        </PreviewBox>
    }
}
