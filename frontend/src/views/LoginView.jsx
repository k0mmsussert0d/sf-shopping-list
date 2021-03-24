import React, {useRef} from 'react';
import {Field, Control, Input, Icon, Button} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faEnvelope, faCheck, faLock} from '@fortawesome/free-solid-svg-icons';
import {Auth} from 'aws-amplify';
import {useAppContext} from '../utils/contextLib';


const LoginView = () => {
  const emailInput = useRef(null);
  const passwordInput = useRef(null);
  const {userHasAuthenticated} = useAppContext();

  const handleSubmit = async event => {
    event.preventDefault();
    const email = emailInput.current.value;
    const password = passwordInput.current.value;

    try {
      await Auth.signIn(email, password);
      console.debug('Logged in');
      userHasAuthenticated(true);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Field>
        <Control iconLeft iconRight>
          <Input
            type="email"
            placeholder="Email"
            ref={emailInput}
          />
          <Icon align="left">
            <FontAwesomeIcon icon={faEnvelope} />
          </Icon>
          <Icon align="right">
            <FontAwesomeIcon icon={faCheck} />
          </Icon>
        </Control>
      </Field>
      <Field>
        <Control iconLeft>
          <Input
            type="password"
            placeholder="Password"
            ref={passwordInput}
          />
          <Icon align="left">
            <FontAwesomeIcon icon={faLock} />
          </Icon>
        </Control>
      </Field>
      <Button.Group>
        <Button color='primary' type='submit'>Log in</Button>
      </Button.Group>
    </form>
  );
};

export default LoginView;
