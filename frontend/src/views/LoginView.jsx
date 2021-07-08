import React, {useState} from 'react';
import {Field, Control, Input, Icon, Button, Column, Help} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faEnvelope, faCheck, faLock} from '@fortawesome/free-solid-svg-icons';
import {Auth} from 'aws-amplify';
import {useAppContext} from '../utils/contextLib';
import {useForm} from 'react-hook-form';


const LoginView = () => {

  const {register, handleSubmit, formState: {errors}} = useForm();
  const {userHasAuthenticated} = useAppContext();
  const [cognitoError, setCognitoError] = useState('');

  const handleSubmitLoginForm = async data => {
    try {
      await Auth.signIn(data.email, data.password);
      console.debug('Logged in');
      userHasAuthenticated(true);
      // TODO: redirect user to lists view
    } catch (e) {
      console.error(e);
      setCognitoError(e.message);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleSubmitLoginForm)}>
      <Field>
        <Control iconLeft iconRight>
          <Input
            type="email"
            placeholder="Email"
            name='email'
            ref={register({
              required: {
                value: true,
                message: 'E-mail is required'
              }
            })}
          />
          <Icon align="left">
            <FontAwesomeIcon icon={faEnvelope} />
          </Icon>
          <Icon align="right">
            <FontAwesomeIcon icon={faCheck} />
          </Icon>
        </Control>
        {errors?.email && <Help color='danger'>{errors.email.message}</Help>}
      </Field>
      <Field>
        <Control iconLeft>
          <Input
            type="password"
            placeholder="Password"
            name='password'
            ref={register({
              required: {
                value: true,
                message: 'Password is required'
              },
            })}
          />
          <Icon align="left">
            <FontAwesomeIcon icon={faLock} />
          </Icon>
        </Control>
        {errors?.password && <Help color='danger'>{errors.email.password}</Help>}
      </Field>
      <Column.Group>
        <Column size='one-third'>
          <Button.Group>
            <Button color='primary' type='submit'>Log in</Button>
          </Button.Group>
        </Column>
        <Column size='auto'>
          {cognitoError && <Help color='danger'>{cognitoError}</Help>}
        </Column>
      </Column.Group>
    </form>
  );
};

export default LoginView;
