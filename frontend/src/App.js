import logo from './logo.svg';
import './App.css';
import Amplify from 'aws-amplify';
import awsconfig from './aws-exports';
import ShoppingListFront from './ShoppingListFront';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from 'react-router-dom';
import Authenticated from './Authenticated';

Amplify.configure(awsconfig);

function App() {
  return (
    <Router>
      <Switch>
        <Route path='/signout'>
          <ShoppingListFront />
        </Route>
        <Route path='/'>
          <Authenticated />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
