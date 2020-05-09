############################################################
#
# This class aims to get the ACT Garbage pickup information
#
# written to be run from AppDaemon for a HASS or HASSIO install
#
# updated: 09/05/2020
# 
############################################################

############################################################
# 
# In the apps.yaml file you will need the following
# updated for your database path, stop ids and name of your flag
#
# act_garbage:
#   module: act_garbage
#   class: Get_ACT_Garbage
#   DAM_FLAG: "input_boolean.check_act_garbage"
#   SUBURB: "CITY"
#   SPLIT_SUBURB: ""
#
############################################################

# import the function libraries
import requests
import datetime
import json
import appdaemon.plugins.hass.hassapi as hass

class Get_ACT_Garbage(hass.Hass):

    # the name of the flag in HA (input_boolean.xxx) that will be watched/turned off
    GAR_FLAG = ""
    SUBURB = ""
    SPLIT_SUBURB = ""
    URL = "https://www.data.act.gov.au/resource/jzzy-44un.json"

    up_sensor = "sensor.act_garbage_last_updated"
    bin_sensor = "sensor.act_garbage_pickup"
    recy_sensor = "sensor.act_recycling_pickup"
    green_sensor = "sensor.act_greenwaste_pickup"
    
    bin_mdi = "mdi:trash-can-outline"
    recy_mdi = "mdi:recycle"
    green_mdi = "mdi:pine-tree-box"

    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    # run each step against the database
    def initialize(self):

        # get the values from the app.yaml that has the relevant personal settings
        self.GAR_FLAG = self.args["GAR_FLAG"]
        self.SUBURB = self.args["SUBURB"]
        self.SPLIT_SUBURB = self.args["SPLIT_SUBURB"]

        # create the original sensor
        self.load()

        # listen to HA for the flag to update the sensor
        self.listen_state(self.main, self.DAM_FLAG, new="on")

    # run the app
    def main(self, entity, attribute, old, new, kwargs):
        """ create the sensor and turn off the flag
            
        """
        # create the sensor with the dam information 
        self.load()
        
        # turn off the flag in HA to show completion
        self.turn_off(self.GAR_FLAG)

    def load(self):
        """ parse the ACT Open Data JSON dataset
        """

        #connect to the website and get the JSON dataset
        url = self.URL
        response = requests.request("GET", url, headers=self.headers, data = self.payload)
        
        #create a sensor to keep track last time this was run
        tim = datetime.datetime.now()
        date_time = tim.strftime("%d/%m/%Y, %H:%M:%S")
        self.set_state(self.up_sensor, state=date_time, replace=True, attributes= {"icon": "mdi:timeline-clock-outline", "friendly_name": "Bin Data last sourced"})

        #convert to json
        jtags = json.loads(response)
        
        #parse the data for the suburb
        for suburbs in jtags:
            this_sub = False
            if self.SPLIT_SUBURB != "":
                if str(suburbs["suburb"]) == self.SUBURB and str(suburbs["split_suburb"]) == self.SPLIT_SUBURB:    
                    this_sub = True
            else:
                if str(suburbs["suburb"]) == self.SUBURB:
                    this_sub = True
                
            if this_sub == True:
                #create the sensors for each of bin type
                self.set_state(self.bin_sensor, state=str(suburbs["garbage_pickup_date"]), replace=True, attributes= {"icon": self.bin_mdi, "friendly_name": "Next Garbage Pickup", "Day": str(suburbs["garbage_collection_day"]))
                self.set_state(self.recy_sensor, state=str(suburbs["recycling_pickup_date"]), replace=True, attributes= {"icon": self.recy_mdi, "friendly_name": "Next Recycling Pickup", "Day": str(suburbs["recyling_collection_day"]))
                self.set_state(self.green_sensor, state=str(suburbs["next_greenwaste_date"]), replace=True, attributes= {"icon": self.green_mdi, "friendly_name": "Next Greenwaste Pickup", "Day": str(suburbs["greenwaste_collection_day"]))
