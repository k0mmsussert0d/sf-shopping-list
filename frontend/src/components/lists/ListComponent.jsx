import React, {useState, useEffect, useRef} from 'react';
import {Box, Title, List, Generic, Input, Button, Icon, Dropdown} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faPlusSquare, faPaperPlane, faTimes, faEdit, faEllipsisH, faShare} from '@fortawesome/free-solid-svg-icons';
import PropTypes from 'prop-types';
import {API} from 'aws-amplify';
import './ListComponent.scss';

const ListComponent = ({id, name, items, newEntry = false}) => {

  const [listName, setListName] = useState('');
  const [newListName, setNewListName] = useState('');
  const [isEditingName, setIsEditingName] = useState(false);
  const listNameInputEl = useRef();
  const [isNameError, setIsNameError] = useState(false);

  const [listItems, setListItems] = useState([]);
  const [isAddingItem, setIsAddingItem] = useState(false);
  const [newItemValue, setNewItemValue] = useState('');
  const itemInputEl = useRef();

  useEffect(() => {
    setListName(name);
    setListItems(items);
    if (newEntry) {
      setListName('');
      setIsEditingName(true);
    }
  }, []);

  useEffect(() => {
    if (isEditingName) {
      listNameInputEl.current.value = listName;
      listNameInputEl.current.focus();
    }
  }, [isEditingName]);

  useEffect(() => {
    if (isAddingItem) {
      itemInputEl.current.focus();
    }
  }, [isAddingItem]);

  const updateList = async ({name = '', items = []}) => {
    const init = {};
    if (name !== '') {
      init.listName = name;
    }
    if (items.length > 0) {
      init.items = items;
    }
    API.put(
      'api',
      `/list/${id}`,
      {
        body: init
      }
    ).then(() => {
      if (newEntry) {
        newEntry = false;
      }
    });
  };

  const renameList = () => {
    if (newListName) {
      setListName(newListName);
      updateList({name: newListName})
        .then(() => {
          setIsEditingName(false);
        });
    }
  };

  const addItemToList = () => {
    if (newItemValue) {
      const newItems = [...listItems, newItemValue];
      setListItems(newItems);
      updateList({items: newItems})
        .then(() => {
          setNewItemValue('');
          itemInputEl.current.value = '';
        });
    }
  };

  const removeItemFromList = index => {
    if (index < listItems.length) {
      const newItems = listItems.filter((_, i) => i !== index);
      setListItems(newItems);
      updateList({items: newItems}).then(() => {});
    }
  };

  return (
    <Box>
      {isEditingName ?
        <Generic as='div' className='list-name-edit'>
          <Input
            type='text'
            placeholder='List name'
            color={isNameError ? 'danger' : ''}
            ref={listNameInputEl}
            onChange={e => setNewListName(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') {
                renameList();
              } else if (e.key === 'Escape') {
                if (newEntry) {
                  setIsNameError(true);
                } else {
                  setIsEditingName(false);
                }
              }
            }
            }
          />
          <Button
            color='success'
            onClick={renameList}
          >
            Apply
          </Button>
        </Generic>
        :
        <Generic as='div' className='list-name'>
          <Title size={3}>{listName}</Title>
          <Icon
            color='light'
            size='large'
            onClick={() => setIsEditingName(true)}
          >
            <FontAwesomeIcon icon={faEdit}/>
          </Icon>
          <Dropdown
            as='span'
            className='item-options-icon'
            align='right'
          >
            <Dropdown.Trigger>
              <Icon
                color='dark'
                size='large'
              >
                <FontAwesomeIcon icon={faEllipsisH} />
              </Icon>
            </Dropdown.Trigger>
            <Dropdown.Menu>
              <Dropdown.Content>
                <Dropdown.Item>
                  <Icon>
                    <FontAwesomeIcon icon={faShare} />
                  </Icon>
                  <span>Share</span>
                </Dropdown.Item>
                <Dropdown.Divider />
                <Dropdown.Item>
                  <Icon color='danger'>
                    <FontAwesomeIcon icon={faTimes} />
                  </Icon>
                  <span>Delete</span>
                </Dropdown.Item>
              </Dropdown.Content>
            </Dropdown.Menu>
          </Dropdown>
        </Generic>}
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
                  onChange={e => setNewItemValue(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      addItemToList();
                    } else if (e.key === 'Escape') {
                      setIsAddingItem(false);
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
  newEntry: PropTypes.bool,
};

export default ListComponent;
