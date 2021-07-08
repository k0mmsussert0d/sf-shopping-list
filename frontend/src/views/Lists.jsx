import React, {useState, useEffect} from 'react';
import {API} from 'aws-amplify';
import ListComponent from '../components/lists/ListComponent';
import {Button} from 'rbx';

const Lists = () => {

  const [lists, setLists] = useState([]);

  const getLists = async () => {
    const lists = await API.get(
      'api',
      '/list',
    );
    setLists(lists);
  };

  const createList = async () => {
    API.post(
      'api',
      '/list',
      {
        body: {
          name: '[unnamed]'
        }
      }
    ).then(res => {
      setLists([...lists, res]);
    });
  };

  useEffect(() => {
    getLists()
      .then(() => {});
  }, []);

  return (
    <>
      {lists.map(l => {
        return (
          <ListComponent
            key={l.id}
            id={l.id}
            name={l.list_name}
            items={l.items}
            newEntry={l.list_name === '[unnamed]'}
          />
        );
      })}
      <Button
        color='primary'
        fullwidth
        onClick={createList}
      >
        Create new list
      </Button>
    </>
  );
};

export default Lists;
