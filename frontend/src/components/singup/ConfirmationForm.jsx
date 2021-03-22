import {Button, Control, Field, Icon, Input} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faKey} from '@fortawesome/free-solid-svg-icons';
import React from 'react';
import {useForm} from 'react-hook-form';
import {Auth} from 'aws-amplify';

// eslint-disable-next-line react/prop-types
const ConfirmationForm = ({newUser}) => {

  const {register, handleSubmit} = useForm();

  const handleSubmitConfirmation = async data => {
    const code = data['confirmationCode'];
    try {
      // eslint-disable-next-line react/prop-types
      await Auth.confirmSignIn(newUser['email'], code);
      // eslint-disable-next-line react/prop-types
      await Auth.signIn(newUser['email'], newUser['password']);
    } catch (e) {
      console.error(e);
    }
  };

  return (

    <form onSubmit={handleSubmit(handleSubmitConfirmation)}>
      <Field>
        <Control iconLeft>
          <Input type="text" placeholder="Code" ref={register({ required: true })} />
          <Icon align="left">
            <FontAwesomeIcon icon={faKey}/>
          </Icon>
        </Control>
      </Field>
      <Button.Group>
        <Button color='primary' fullwidth type='submit'>Confirm</Button>
      </Button.Group>
    </form>
  );
};

export default ConfirmationForm;
