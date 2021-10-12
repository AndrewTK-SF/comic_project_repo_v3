# Maarvel Comics Library Manager
This web app can be paired with a standard barcode scanner and used to scan the barcode of Marvel comic book which automatically enters the issue into the user's issue library.  When the barcode is scanned, an API request is sent to the Marvel developer server retrieving cover art, issue release date and creator info (e.g. writer and artist credits).  The app tracks "favorited" issues across users and displays the "most favorited" issue on the home page for all users.

Built with
* Django
* Bootstrap

Get free API keys at https://developer.marvel.com/

Install python-dotenv
* pip install python-dotenv

Install Requests
* pip install requests

Example UPC codes for testing
* 75960609732600211
* 75960609413400111
* 75960609467700211

In the future I would like to add the following features
* App displays the writer(s) and artist(s) of a user's favorited issues
* App displays the writer(s) and artist(s) of favorited issues across users

