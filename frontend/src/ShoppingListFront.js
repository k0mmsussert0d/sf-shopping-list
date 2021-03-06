import { AmplifySignOut, withAuthenticator } from '@aws-amplify/ui-react';

const ShoppintListFront = () => {
    <div>
        <AmplifySignOut />
        My app
    </div>
}

export default withAuthenticator(ShoppintListFront);