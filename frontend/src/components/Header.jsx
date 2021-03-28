import React from 'react';
import { Navbar, Button } from 'rbx';
import {useAppContext} from '../utils/contextLib';
import {Auth} from 'aws-amplify';
import {Link, Redirect} from 'react-router-dom';
import './Header.scss';


const Header = () => {

  const {isAuthenticated, userHasAuthenticated} = useAppContext();

  const performLogout = async () => {
    await Auth.signOut();
    userHasAuthenticated(false);
    return <Redirect to='/' />;
  };

  const signedOutOptions = () => {
    return (
      <Navbar.Menu>
        <Navbar.Segment align="end">
          <Navbar.Item as='div'>
            <Button.Group>
              <Link to='/signup'>
                <Button color="primary">
                  <strong>Sign up</strong>
                </Button>
              </Link>
              <Link to='/login'>
                <Button color="light">Log in</Button>
              </Link>
            </Button.Group>
          </Navbar.Item>
        </Navbar.Segment>
      </Navbar.Menu>
    );
  };

  const signedInOptions = () => {
    return (
      <Navbar.Menu>
        <Navbar.Segment align="start">
          <Link to='/lists'>
            <Navbar.Item as='div'>Lists</Navbar.Item>
          </Link>
          <Navbar.Item>Profile</Navbar.Item>
        </Navbar.Segment>
        <Navbar.Segment align="end">
          <Navbar.Item>
            <Button.Group>
              <Button color="primary" onClick={performLogout}>
                <strong>Log out</strong>
              </Button>
            </Button.Group>
          </Navbar.Item>
        </Navbar.Segment>
      </Navbar.Menu>
    );
  };

  return (
    <Navbar>
      <Navbar.Brand>
        <Link to='/'>
          <Navbar.Item as='div'>
            <img
              src="https://bulma.io/images/bulma-logo.png"
              alt=""
              role="presentation"
              width="112"
              height="28"
            />
          </Navbar.Item>
        </Link>
        <Navbar.Burger />
      </Navbar.Brand>
      {isAuthenticated ? signedInOptions() : signedOutOptions()}
    </Navbar>
  );
};

export default Header;
