import React from 'react';
import {Box, Title} from 'rbx';
import PropTypes from 'prop-types';

const List = ({name, items}) => {

  return (
    <Box>
      <Title size={3}>{name}</Title>
    </Box>
  );
};

List.propTypes = {
  name: PropTypes.string,
  items: PropTypes.object
};

export default List;
