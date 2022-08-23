import React from 'react';
import PropTypes from 'prop-types';

import styled from 'styled-components';

const SelectContainer = styled.div`
  position: relative;
`;

const Select = styled.select`
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  font-size: 1rem;
  padding: 1em 4em 1em 1.5em;
  background: #ffffff;
  border: 0;
`;

const CustomArrow = styled.span`
  position: absolute;
  top: 0;
  right: 0;
  display: block;
  background-color: #3b3c47;
  height: 100%;
  width: 4em;
  pointer-events: none;
`;

const SelectField = ({ items, selected }) => {
  return (
    <SelectContainer>
      <Select>
        {items && Object.entries(items).map(([label, value]) => <option value={value}>{label}</option>)}
        <CustomArrow></CustomArrow>
      </Select>

    </SelectContainer >
  )
}

SelectField.propTypes = {
  items: PropTypes.object.isRequired,
  defaultSected: PropTypes.string
}

export default SelectField
