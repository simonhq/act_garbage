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
#   GAR_FLAG: "input_boolean.check_act_garbage"
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
    
    bin_bin_tod = "binary_sensor.act_garbage_today"
    bin_bin_tom = "binary_sensor.act_garbage_tomorrow"
    rec_bin_tod = "binary_sensor.act_recycling_today"
    rec_bin_tom = "binary_sensor.act_recycling_tomorrow"
    gre_bin_tod = "binary_sensor.act_greenwaste_today"
    gre_bin_tom = "binary_sensor.act_greenwaste_tomorrow"

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
        self.SUBURB = self.args["SUBURB"].upper()
        self.SPLIT_SUBURB = self.args["SPLIT_SUBURB"].capitalize()

        # create the original sensor
        self.load()

        # listen to HA for the flag to update the sensor
        self.listen_state(self.main, self.GAR_FLAG, new="on")

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
        tomorrow = tim - datetime.timedelta(days=-1)
        date_time = tim.strftime("%d/%m/%Y, %H:%M:%S")
        date_date = tim.strftime("%d/%m/%Y")
        tomorrow_date = tomorrow.strftime("%d/%m/%Y")
        self.set_state(self.up_sensor, state=date_time, replace=True, attributes= {"icon": "mdi:timeline-clock-outline", "friendly_name": "Bin Data last sourced", "Suburb": self.SUBURB, "Split-Suburb": self.SPLIT_SUBURB })
            
        #convert to json
        jtags = json.loads(response.text)
        
        #err flag
        sub_found = False
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
                sub_found = True
                #create the sensors for each of bin type
                self.set_state(self.bin_sensor, state=str(suburbs["garbage_pickup_date"]), replace=True, attributes= {"icon": self.bin_mdi, "friendly_name": "Next Garbage Pickup", "Day": str(suburbs["garbage_collection_day"]), "Collection Week": str(suburbs["collection_week"]) })
                self.set_state(self.recy_sensor, state=str(suburbs["recycling_pickup_date"]), replace=True, attributes= {"icon": self.recy_mdi, "friendly_name": "Next Recycling Pickup", "Day": str(suburbs["recycling_collection_day"]), "Collection Week": str(suburbs["collection_week"])})
                self.set_state(self.green_sensor, state=str(suburbs["next_greenwaste_date"]), replace=True, attributes= {"icon": self.green_mdi, "friendly_name": "Next Greenwaste Pickup", "Day": str(suburbs["greenwaste_collection_day"]), "Collection Week": str(suburbs["greenwaste_collection_week"])})
            
                #binary values for bin
                if str(suburbs["garbage_pickup_date"]) == date_date: 
                    bin_tod_state = True
                    bin_tom_state = False
                elif str(suburbs["garbage_pickup_date"]) == tomorrow_date: 
                    bin_tod_state = False
                    bin_tom_state = True
                else:
                    bin_tod_state = False
                    bin_tom_state = False
                #binary values for rec
                if str(suburbs["recycling_pickup_date"]) == date_date:
                    rec_tod_state = True
                    rec_tom_state = False
                elif str(suburbs["recycling_pickup_date"]) == tomorrow_date:
                    rec_tod_state = False
                    rec_tom_state = True
                else:
                    rec_tod_state = False
                    rec_tom_state = False
                #binary values for greenwaste
                if str(suburbs["next_greenwaste_date"]) == date_date:
                    gre_tod_state = True
                    gre_tom_state = False
                elif str(suburbs["next_greenwaste_date"]) == tomorrow_date:
                    gre_tod_state = False
                    gre_tom_state = True
                else:
                    gre_tod_state = False
                    gre_tom_state = False

        #if nothing can be found
        if sub_found == False:
            #clear the sensors so that they no an error has occured
            self.set_state(self.bin_sensor, state="No Suburb", replace=True, attributes= {"icon": self.bin_mdi, "friendly_name": "Next Garbage Pickup" })
            self.set_state(self.recy_sensor, state="No Suburb", replace=True, attributes= {"icon": self.recy_mdi, "friendly_name": "Next Recycling Pickup" })
            self.set_state(self.green_sensor, state="No Suburb", replace=True, attributes= {"icon": self.green_mdi, "friendly_name": "Next Greenwaste Pickup"})
            bin_tod_state = False
            bin_tom_state = False
            rec_tod_state = False
            rec_tom_state = False
            gre_tod_state = False
            gre_tom_state = False


        #finally create the binary sensors
        self.set_state(self.bin_bin_tod, state=bin_tod_state, replace=True, attributes= {"icon": self.bin_mdi, "friendly_name": "Bin Pickup Today" })
        self.set_state(self.bin_bin_tom, state=bin_tom_state, replace=True, attributes= {"icon": self.bin_mdi, "friendly_name": "Bin Pickup Tomorrow" })
        self.set_state(self.rec_bin_tod, state=rec_tod_state, replace=True, attributes= {"icon": self.recy_mdi, "friendly_name": "Recycling Pickup Today" })
        self.set_state(self.rec_bin_tom, state=rec_tom_state, replace=True, attributes= {"icon": self.recy_mdi, "friendly_name": "Recycling Pickup Tomorrow" })
        self.set_state(self.gre_bin_tod, state=gre_tod_state, replace=True, attributes= {"icon": self.green_mdi, "friendly_name": "Green Waste Pickup Today" })
        self.set_state(self.gre_bin_tom, state=gre_tom_state, replace=True, attributes= {"icon": self.green_mdi, "friendly_name": "Green Waste Pickup Tomorrow" })
