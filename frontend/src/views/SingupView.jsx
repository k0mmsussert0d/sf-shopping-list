import React, {useState} from 'react';
import ConfirmationForm from '../components/singup/ConfirmationForm';
import SignUpForm from '../components/singup/SignUpForm';

const SingupView = () => {
  const [newUser, setNewUser] = useState(null);

  return (
    <>
      {newUser !== null ?
        <ConfirmationForm
          setNewUser={setNewUser}
        />
        :
        <SignUpForm
          newUser={newUser}
        />
      }
    </>
  );
};

export default SingupView;
