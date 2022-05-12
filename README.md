# Dublin Bikes Web Application

This repository is submitted as partial fullfilment of the Software Enginering (COMP30830) module for the MSc of Computer Science (conversion) course. The purpose of this project is to employ the agile scrum methodology of development to serve a web application. 


## Applciation architecture
The combination of the web framework known as Flask and Amazon Web Services (AWS) provides a majority of the structure required to serve the web application for public use. The web application functions as a simple way to display relevant information for users who wish to rent a Dublin bike. For one to view data there must be data to view, this is where AWS first comes into play. The data to be displayed for this web service was Dublin bike rental station data and weather data for the surrounding area. This data was scraped from the respective websites (jcdecaux and openweather) and saved to a MySQL database running in Amazons RDS cloud.

Importing Flask into a python file provides the web framework used to navigate the various methods implemented with the variety of languages required to develop a successful web application. The App.py file speaks to the MySQL database when information is needed and provides said information to the JavaScript file for implementation and presenting to the html file for formatting. While Google developer provides the tools for displaying the map and associated features.

The application is deployed on Amazons EC2 service, which is a virtual machine running on the cloud. This virtual machine runs the app.py file which with the combination of flask, gunicorn and nginx deploys the application for public use.
