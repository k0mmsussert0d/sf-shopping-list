import React, {useState, useEffect, useRef} from 'react';
import {Box, Title, List, Generic, Input, Button, Icon} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faPlusSquare, faPaperPlane, faTimes} from '@fortawesome/free-solid-svg-icons';
import PropTypes from 'prop-types';

import './ListComponent.scss';
import {API} from 'aws-amplify';

const ListComponent = ({id, name, items}) => {

  const [listItems, setListItems] = useState([]);
  const [isAddingItem, setIsAddingItem] = useState(false);
  const [newItemValue, setNewItemValue] = useState('');
  const itemInputEl = useRef();

  useEffect(() => {
    setListItems(items);
  }, []);

  useEffect(() => {
    if (isAddingItem) {
      itemInputEl.current.focus();
    }
  }, [isAddingItem]);

  const updateList = async items => {
    await API.put(
      'api',
      `/list/${id}`,
      {
        body: items
      }
    );
  };

  const addItemToList = () => {
    if (newItemValue) {
      const newItems = [...listItems, newItemValue];
      setListItems(newItems);
      updateList(newItems)
        .then(() => {
          setNewItemValue('');
        });
    }
  };

  const removeItemFromList = index => {
    if (index < listItems.length) {
      const newItems = listItems.filter((_, i) => i !== index);
      setListItems(newItems);
      updateList(newItems).then(() => {});
    }
  };

  return (
    <Box>
      <Title size={3}>{name}</Title>
      <List>
        {listItems.map((i, idx) => {
          return (
            <List.Item key={name + '_' + idx}>
              <Generic as='span' className='item-label'>
                {i}
              </Generic>
              <Generic as='span' className='item-remove-icon'>
                <Icon color='danger' onClick={() => removeItemFromList(idx)}>
                  <FontAwesomeIcon icon={faTimes} />
                </Icon>
              </Generic>
            </List.Item>
          );
        })}
        <List.Item>
          <Generic as='div' className='item-block'>
            {isAddingItem ?
              <>
                <Input
                  type='text'
                  placeholder='New item'
                  ref={itemInputEl}
                  onChange={e => setNewItemValue(e.current.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      addItemToList();
                    }
                  }}
                />
                <Button type='submit'>
                  <Icon size='small'>
                    <FontAwesomeIcon icon={faPaperPlane} />
                  </Icon>
                </Button>
              </>
              :
              <Generic onClick={() => {
                setIsAddingItem(!isAddingItem);
              }}>
                <Icon color='success'>
                  <FontAwesomeIcon icon={faPlusSquare} />
                </Icon>
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
  id: PropTypes.string,
  name: PropTypes.string,
  items: PropTypes.array,
};

export default ListComponent;
