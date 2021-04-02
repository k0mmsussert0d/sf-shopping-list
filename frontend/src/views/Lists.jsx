import React, {useState, useEffect} from 'react';
import {API} from 'aws-amplify';
import ListComponent from '../components/lists/ListComponent';

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
          <ListComponent key={l.id} id={l.id} name={l.list_name} items={l.items} />
        );
      })}
    </>
  );
};

export default Lists;
