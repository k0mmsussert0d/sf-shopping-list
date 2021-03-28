import React, {useState, useEffect} from 'react';
import {API} from 'aws-amplify';
import List from '../components/lists/List';

const Lists = () => {

  const [lists, setLists] = useState([]);

  useEffect(() => {
    const getLists = async () => {
      const lists = await API.get(
        'api',
        '/list',
      );
      setLists(lists);
    };
    getLists();
  }, []);

  return (
    <>
      {lists.map(l => {
        return (
          <List key={l.id} name={l.name} items={{}} />
        );
      })}
    </>
  );
};

export default Lists;
