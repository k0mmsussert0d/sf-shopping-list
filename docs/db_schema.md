# Database table schemas

## ListsDynamoDbTable

Single item in this table represents *list* (called `lists` to avoid naming conflict in the code) entity.

| id | user_id | created_at | list_name | items | guests |
|----|---------|------------|-----------|-------|--------|
| PK |
|    | PK      | SK

 - **`id`** (string) - unique item identifier, seen by user
 - **`user_id`** (string) - OpenID identifier of item creator
 - **`created_at`** (integer | time) - creation time
 - `list_name` (string) - item name
 - `items` (Array[string]) - content (list of strings)
 - `guests` (Array[string]) - OpenID of users allowed to modify the entity

## UserToListsDynamoDbTable

This table stores information on which *lists* user has access to.

| user_id | lists  |
|---------|--------|
| PK      

- **`user_id`** (string) - OpenID identifier of user
- **`lists`** (Array[string]) - list of lists user has access to

## ListsSharingDynamoDbTable

This table stores data on currently active sharing invitations.

| id | list_id | valid_until |
|----|---------|-------------|
| PK |

- **`id`** (string) - unique invitation identifier, visible for user
- **`list_id`** (string) - list id this invitation gives access to
- `valid_for` (ttl) - invitation cannot be used after that time
