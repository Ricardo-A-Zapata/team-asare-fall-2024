# REQUIREMENTS 

The journal will:
    - Create, Read, Update, and Delete Users and their attributes
    - Give users roles to ensure proper permissions
    - Have a [masthead] (https://publishdrive.com/glossary-what-is-a-masthead.html#:~:text=A%20masthead%20is%20a%20place,magazine%2C%20or%20other%20printed%20material.)
    - Have a guideline page for making submissions
    - Be accessible on the web independant of device
    - Have a title, author, text content, etc

## PROGRESS 

Currently, we have:
    - Created a MongoDB, NoSQL database to store Users, Manuscripts, Mastheads, Text, and Roles
    - Connected to the remote database using the connection string given by MongoDB, hiding sensitive info in our environment variables
    - Created endpoints to perform CRUD operations on the database, which maintain database sterility and foreign key constraints
    - Implemented thorough tests for each endpoint created, using latest Pytest and unittest features such as patches and fixtures

Within this week (Jan. 27th -> Jan 31st), we have:
    - Fixed broken tests
    - Ensured we had all neccassary endpoints for our database collections

## GOALS 

For the future, we'd like to:
    - Design the webflow of our journal
        - Determine what actions will be available to certain users on different screens
            - Understand how we will stop certain users from invoking certain actions
        - Figure out which screens link to each other, and what their name will be
    - Draw up some mockups for what we want each screen to look like
    - Gather some test data to validate our backend endpoints