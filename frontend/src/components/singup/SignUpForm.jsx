import {useState} from 'react';
import {Button, Control, Field, Icon, Input, Help, Column} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faUser, faEnvelope, faLock} from '@fortawesome/free-solid-svg-icons';
import React from 'react';
import {useForm} from 'react-hook-form';
import {Auth} from 'aws-amplify';
import PropTypes from 'prop-types';

const SignUpForm = ({setNewUser}) => {

  const {register, handleSubmit, getValues, formState: {errors}} = useForm();
  const [cognitoError, setCognitoError] = useState('');

  const handleSubmitRegistrationForm = async data => {
    if (data['password'] !== data['confirm-password']) {
      return;
    }

    try {
      await Auth.signUp({
        username: data.email,
        password: data.password,
        attributes: {
          nickname: data.nickname
        }
      });
      setNewUser({
        email: data.email,
        password: data.password
      });
    } catch (e) {
      console.error(e);
      setCognitoError(e?.message);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleSubmitRegistrationForm)}>
      <Field>
        <Control iconLeft iconRight>
          <Input type="text" placeholder='Your name (e.g Max)' name='nickname' ref={register({
            required: {
              value: true,
              message: 'Name is required'
            }
          })}/>
          <Icon align="left">
            <FontAwesomeIcon icon={faUser}/>
          </Icon>
        </Control>
        {errors?.email && <Help color='danger'>{errors.email.message}</Help>}
      </Field>
      <Field>
        <Control iconLeft iconRight>
          <Input type="email" placeholder="Email" name='email' ref={register({
            required: {
              value: true,
              message: 'Email is required'
            }
          })}/>
          <Icon align="left">
            <FontAwesomeIcon icon={faEnvelope}/>
          </Icon>
        </Control>
        {errors?.email && <Help color='danger'>{errors.email.message}</Help>}
      </Field>
      <Field>
        <Control iconLeft>
          <Input type="password" placeholder="Password" name='password' ref={register({
            required: {
              value: true,
              message: 'Password is required'
            },
            pattern: {
              value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\^$*.[\]{}()?\-“!@#%&/,><’:;|_~`])\S{8,99}$/,
              message: 'Password must have at least 8 characters, including: at least one uppercase character,' +
                    'at least one lowercase character, at least one digit and at least one special character'
            }
          })}/>
          <Icon align="left">
            <FontAwesomeIcon icon={faLock}/>
          </Icon>
        </Control>
        {errors?.password && <Help color='danger'>{errors.password.message}</Help>}
      </Field>
      <Field>
        <Control iconLeft>
          <Input type="password" placeholder="Confirm password" name='confirm-password' ref={register({
            required: {
              value: true,
              message: 'Password is required'
            },
            validate: pw => {
              const {password} = getValues();
              return pw === password || 'Passwords don\'t match';
            }
          })}/>
          <Icon align="left">
            <FontAwesomeIcon icon={faLock}/>
          </Icon>
        </Control>
        {errors['confirm-password'] && <Help color='danger'>{errors['confirm-password'].message}</Help>}
      </Field>
      <Column.Group>
        <Column size='one-third'>
          <Button.Group>
            <Button color='primary' type='submit'>Sign up</Button>
          </Button.Group>
        </Column>
        <Column size='auto'>
          {cognitoError && <Help color='danger'>{cognitoError}</Help>}
        </Column>
      </Column.Group>
    </form>
  );
};

SignUpForm.propTypes = {
  setNewUser: PropTypes.func
};

export default SignUpForm;
