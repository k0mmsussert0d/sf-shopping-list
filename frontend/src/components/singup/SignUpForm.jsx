import {Button, Control, Field, Icon, Input} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faCheck, faEnvelope, faLock} from '@fortawesome/free-solid-svg-icons';
import React from 'react';
import {useForm} from 'react-hook-form';
import {Auth} from 'aws-amplify';

// eslint-disable-next-line react/prop-types
const SignUpForm = ({setNewUser}) => {

  const {register, handleSubmit, getValues} = useForm();

  const handleSubmitRegistrationForm = async data => {
    if (data['password'] !== data['confirm-password']) {
      return;
    }

    try {
      const newUser = await Auth.signUp({
        username: data.email,
        password: data.password,
      });
      setNewUser(newUser);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleSubmitRegistrationForm)}>
      <Field>
        <Control iconLeft iconRight>
          <Input type="email" placeholder="Email" name='email' ref={register({ required: true })}/>
          <Icon align="left">
            <FontAwesomeIcon icon={faEnvelope}/>
          </Icon>
          <Icon align="right">
            <FontAwesomeIcon icon={faCheck}/>
          </Icon>
        </Control>
      </Field>
      <Field>
        <Control iconLeft>
          <Input type="password" placeholder="Password" name='password' ref={register({
            required: true,
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
      </Field>
      <Field>
        <Control iconLeft>
          <Input type="password" placeholder="Confirm password" name='confirm-password' ref={register({
            required: true,
            pattern: {
              value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\^$*.[\]{}()?\-“!@#%&/,><’:;|_~`])\S{8,99}$/,
              message: 'Password must have at least 8 characters, including: at least one uppercase character,' +
                    'at least one lowercase character, at least one digit and at least one special character'
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
      </Field>
      <Button.Group>
        <Button color='primary' type='submit'>Sign up</Button>
      </Button.Group>
    </form>
  );
};

export default SignUpForm;
