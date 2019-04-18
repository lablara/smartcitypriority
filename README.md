# smartcitypriority
Python3 implementation of temperature sensor nodes (tempsensor) and a central controller (CPM), performing prioritization

This implementation is a proof-of-concept of the definitions presented in the article "A Prioritization Approach for Optimization of Multiple Concurrent Sensing Applications in Smart Cities"

The sensor node is executed through the file "tempsensor.py". It requires two additional libraries, which can be installed through the following commands:

pip3 install Adafruit_DHT

pip3 install wiringpi

The CPM is executed through the file "cpm.py".
All configuration tables are defined through a specific txt file in the directoy "tables\". So, there are the "context.txt" for the CT and a subdirectoy "events\", which defines the events priority for each value of a. For exemple, for a=1, the file tables\events\1.txt must to be configured

------------
Author Daniel G. Costa 

danielgcosta@uefs.br
http://lara.uefs.br
http://www.uefs.br/danielgcosta
