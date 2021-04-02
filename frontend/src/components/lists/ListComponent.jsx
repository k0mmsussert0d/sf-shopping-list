import React, {useState, useEffect, useRef} from 'react';
import {Box, Title, List, Generic, Input, Button, Icon} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faPlusSquare, faPaperPlane} from '@fortawesome/free-solid-svg-icons';
import PropTypes from 'prop-types';

import './ListComponent.scss';
import {API} from 'aws-amplify';

const ListComponent = ({id, name, items}) => {

  const [listItems, setListItems] = useState([]);
  const [isAddingItem, setIsAddingItem] = useState(false);
  const itemInputEl = useRef(null);

  useEffect(() => {
    setListItems(items);
  }, []);


  const addItemToList = () => {
    const updateList = async items => {
      await API.put(
        'api',
        `/list/${id}`,
        {
          body: items
        }
      );
    };

    const item = itemInputEl.current.value;
    const newItems = [...listItems, item];
    setListItems(newItems);
    updateList(newItems);
  };

  return (
    <Box>
      <Title size={3}>{name}</Title>
      <List>
        {listItems.map((i, idx) => {
          return (
            <List.Item key={idx}>{i}</List.Item>
          );
        })}
        <List.Item>
          <Generic as='div' className='item-block'>
            {isAddingItem ?
              <>
                <Input type='text' placeholder='New item' ref={itemInputEl} />
                <Button onClick={addItemToList}>
                  <Icon size='small'>
                    <FontAwesomeIcon icon={faPaperPlane} />
                  </Icon>
                </Button>
              </>
              :
              <Generic onClick={() => setIsAddingItem(!isAddingItem)}>
                <FontAwesomeIcon icon={faPlusSquare} />
                <Generic as='span' className='item-name'>Add new item</Generic>
              </Generic>
            }
          </Generic>
        </List.Item>
      </List>
    </Box>
  );
};

ListComponent.propTypes = {
  id: PropTypes.number,
  name: PropTypes.string,
  items: PropTypes.array,
};

export default ListComponent;
