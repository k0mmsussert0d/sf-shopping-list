import './App.css';
import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from 'react-router-dom';

import Header from './components/Header';
import 'rbx/index.css';


function App() {
  return (
    <Router>
      <Header />
      <Switch>
        <Route path='/lists'></Route>
        <Route path='/profile'></Route>
        <Route path='/'></Route>
      </Switch>
    </Router>
  );
}

export default App;
