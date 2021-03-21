import './App.css';
import React, {useState, useEffect} from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from 'react-router-dom';
import {Generic} from 'rbx';

import Header from './components/Header';
import LoginView from './views/LoginView';
import 'rbx/index.css';
import { AppContext } from './utils/contextLib';
import {Auth} from 'aws-amplify';


function App() {

  const [isAuthenticated, userHasAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(true);

  useEffect(() => {
    const onLoad = async() => {
      try {
        await Auth.currentSession();
        userHasAuthenticated(true);
      } catch (e) {
        if (e !== 'No current user') {
          console.error(e);
        }
      }
      setIsAuthenticating(false);
    };

    onLoad();
  }, []);

  return (
    <AppContext.Provider value={{ isAuthenticated, userHasAuthenticated }}>
      <Router>
        <Header />
        <Switch>
          <Generic as='div' className='main-wrapper'>
            <Route path='/login'>
              <LoginView />
            </Route>
            <Route path='/lists'></Route>
            <Route path='/profile'></Route>
          </Generic>
        </Switch>
      </Router>
    </AppContext.Provider>
  );
}

export default App;
