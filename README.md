## Vancouver Transit Analyzer

#### Map out which transit stops in Vancouver have the longest delays. 
<p align="center">
  <img src="https://github.com/slehmann1/VancouverTransit/blob/main/resources/sampleMap.gif?raw=true" />
</p>

**Try it out [here](https://samuellehmann.com/transit).**

Full stack web application built with Django and PostgreSQL that pulls data from [Translink's GTFS realtime data](https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources/gtfs). Data is polled every 10 minutes. Deployed with Docker, AWS EC2, Gunicorn, Traefik, and Redis. 

**Dependencies:**

Pandas, numpy, pytest, bootstrap, leaflet. 
