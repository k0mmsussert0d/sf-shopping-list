import {Button, Control, Field, Icon, Input, Generic, Help} from 'rbx';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faKey} from '@fortawesome/free-solid-svg-icons';
import React, {useState} from 'react';
import {useForm} from 'react-hook-form';
import {Auth} from 'aws-amplify';
import PropTypes from 'prop-types';

const ConfirmationForm = ({newUser}) => {

  const {register, handleSubmit} = useForm();
  const [cognitoError, setCognitoError] = useState('');

  const handleSubmitConfirmation = async data => {
    const code = data['code'];
    try {
      await Auth.confirmSignUp(newUser['email'], code);
      await Auth.signIn(newUser['email'], newUser['password']);
    } catch (e) {
      console.error(e);
      setCognitoError(e.message);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleSubmitConfirmation)}>
      <Field>
        <Control iconLeft>
          <Input type="text" placeholder="Code" name='code' ref={register({required: true})}/>
          <Icon align="left">
            <FontAwesomeIcon icon={faKey}/>
          </Icon>
        </Control>
      </Field>
      <Generic>
        <Button.Group>
          <Button color='primary' fullwidth type='submit'>Confirm</Button>
        </Button.Group>
        {cognitoError && <Help color='danger'>{cognitoError}</Help>}
      </Generic>
    </form>
  );
};

ConfirmationForm.propTypes = {
  newUser: PropTypes.object
};

export default ConfirmationForm;
