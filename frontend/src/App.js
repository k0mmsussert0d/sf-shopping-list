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
import SingupView from './views/SingupView';
import Lists from './views/Lists';


function App() {

  const [isAuthenticated, userHasAuthenticated] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  useEffect(() => {
    const onLoad = async() => {
      setIsAuthenticating(true);
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
        <Generic as='div' className='main-wrapper'>
          <Switch>
            <Route path='/login'>
              <LoginView />
            </Route>
            <Route path='/signup'>
              <SingupView />
            </Route>
            <Route path='/lists'>
              <Lists />
            </Route>
            <Route path='/profile'></Route>
          </Switch>
        </Generic>
      </Router>
    </AppContext.Provider>
  );
}

export default App;
