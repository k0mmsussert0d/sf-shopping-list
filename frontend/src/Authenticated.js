import { Auth } from "aws-amplify"
import { useState, useEffect } from "react"

const Authenticated = () => {

    const [user, setUser] = useState(null);
    useEffect(() => {
        const fetchUser = async () => {
            setUser(await Auth.currentAuthenticatedUser());
        }

        fetchUser();
    }, [])

    return (
        <div>
            {JSON.stringify(user, null, 2) ?? 'No auth'}
        </div>
    );
}

export default Authenticated;