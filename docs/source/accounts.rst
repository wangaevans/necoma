Authentication (User Accounts)
=============================

This section documents the user authentication views provided by the `accounts` module. These views handle user-related actions such as logging in, logging out, and registration for network admins or operators. Each view is explained in detail to assist new users in understanding their purpose and usage.

Sign Up Network Admin
---------------------
This view allows a network admin or operator to sign up for an account. It presents a sign-up form, validates the submitted data, and creates a new user account upon successful validation.

.. autofunction:: accounts.views.network_admin_signup

Sign In Network Admin
---------------------
This view handles the login process for network admins or operators. It authenticates the user's credentials and logs them in if the authentication is successful.

.. autofunction:: accounts.views.network_admin_login

Log Out Network Admin
---------------------
This view logs out the currently authenticated network admin or operator. It ends the user's session and redirects them to the home page.

.. autofunction:: accounts.views.logout_admin
