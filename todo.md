# Tasks to-do

## Flows

- User can create an account
- User can verify their email address
- User can login
- User can logout
- User can reset their password
- User can change their password
- User can add a new relationship
- User can edit a relationship
- User can get their details with relationship status
- User can update their profile

## Api

### User can crete an account

- [x] Register endpoint

### User can verify their email address

- [x] Verify email endpoint

### User can login

- [x] Login endpoint

### User can logout

- [x] Logout endpoint

### User can reset their password

- [x] Forgot password endpoint
- [x] Reset password endpoint

### User can change their password

- [x] Change password endpoint

### User can update their profile

- [x] Update profile endpoint

### User can add a new relationship

- [ ] Add relationship endpoint

    Psuedocode algorithm

    1. User sends a request to add a relationship by adding the phone numbers of the person they want to add.

        Checks

        1. User is logged in
        2. User is not adding themselves
        3. User is not already in a relationship with anyone
        4. All phone numbers are valid
        5. None of the phone numbers are already in a relationship

    2. Create a new relationship, set to pending
    3. Provide the other party's email address
    4. Generate a single validation link for the other party to verify the relationship phone numbers
        - The link should be valid for 24 hours

    5. Send the email to the other party, they user can also copy the link and send it to the other party

    6. If the other party clicks the link, they are redirected to a page where they can verify the phone numbers

    7. If the other party verifies the phone numbers, the relationship is set to active and the other party is added to the relationship

    8. If the other party fails to verify the phone numbers, the relationship is set to cancelled. The creator of the relationship is notified via email.

    9. [Optional*] If any of the verified phone numbers belongs to a user with an account, they are added to the relationship.

- [ ] Endpoint for the website to use to send and resend verification otp's to phone numbers to verify

- [ ] Endpoint for the website to use to verify the otp's

- After everything is verified, the relationship is set to active ( both parties have verified ) and the partner is added to the relationship. They should be notified via email.
  - Maybe use model signals to send the email and check if all the phone numbers are verified

### User can edit a relationship

- [ ] Endpoint for a user to cancel a relationship

    Psuedocode algorithm

    1. User sends a request to cancel a relationship
    2. The relationship is set to cancelled
    3. The other party is notified via email


### User can get their details with relationship status

- [ ] Endpoint for a user to get their details with relationship status

    Psuedocode algorithm

    1. User sends a request to get their details with relationship status
    2. The user's details are returned with the relationship status
