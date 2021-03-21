import React, {useState} from 'react';
import { Navbar, Button } from 'rbx';


const Header = () => {

  const [loggedIn, setLoggedIn] = useState(false);

  const signedOutOptions = () => {
    return (
      <Navbar.Menu>
        <Navbar.Segment align="end">
          <Navbar.Item>
            <Button.Group>
              <Button color="primary">
                <strong>Sign up</strong>
              </Button>
              <Button color="light">Log in</Button>
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
          <Navbar.Item>Lists</Navbar.Item>
          <Navbar.Item>Profile</Navbar.Item>

        </Navbar.Segment>

        <Navbar.Segment align="end">
          <Navbar.Item>
            <Button.Group>
              <Button color="primary">
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
        <Navbar.Item href="#">
          <img
            src="https://bulma.io/images/bulma-logo.png"
            alt=""
            role="presentation"
            width="112"
            height="28"
          />
        </Navbar.Item>
        <Navbar.Burger />
      </Navbar.Brand>
      {signedInOptions()}
    </Navbar>
  );
};

export default Header;