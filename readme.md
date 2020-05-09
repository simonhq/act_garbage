# Australian Capital Territory Garbage/Recycling/Greenwaste Pickup
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

_Creates sensors for Home Assistant with the collection information for the bins within a suburb in the ACT_


## Lovelace Examples

![Example of the entities in Lovelace](https://github.com/simonhq/act_garbage/blob/master/act_garbage_entities.PNG)

![An Entity has date informaiton](https://github.com/simonhq/act_garbage/blob/master/act_garbage_entity.PNG)

## Installation

This app is best installed using
[HACS](https://github.com/custom-components/hacs), so that you can easily track
and download updates.

Alternatively, you can download the `act_garbage` directory from inside the `apps` directory here to your
local `apps` directory, then add the configuration to enable the `act_garbage` module.

## How it works

The [ACT Open Data](https://www.data.act.gov.au/Community-Services/ACT-Suburb-Next-Garbage-Recycling-and-Green-Waste-/jzzy-44un) site provides this information, 
this just makes the information available as sensors in HA.

As this is non time critical sensor, it does not get the information on a set time schedule, but watches a input_boolean that you 
specify for when to update the sensor. You can obviously automate when you want that input_boolean to turn on.

### To Run

You will need to create an input_boolean entity to watch for when to update the sensor. When this
`input_boolean` is turned on, whether manually or by another automation you
create, the scraping process will be run to create/update the sensor.

## AppDaemon Libraries

Please add the following packages to your appdaemon 4 configuration on the supervisor page of the add-on.

``` yaml
system_packages: []
python_packages:
init_commands: []
```

No specific packages are required for this app.

## App configuration

In the apps.yaml file in the appdaemon/apps directory - 

```yaml
act_garbage:
  module: act_garbage
  class: Get_ACT_Garbage
  GAR_FLAG: "input_boolean.check_act_garbage"
  SUBURB: "CITY"
  SPLIT_SUBURB: ""
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | `act_garbage`
`class` | False | string | | `Get_ACT_Garbage`
`GAR_FLAG` | False | string | | The name of the flag in HA for triggering this sensor update - e.g. input_boolean.check_act_garbage
`SUBURB` | False | string | | The name of the suburb to get the information for
`SPLIT_SUBURB` | True | string | | A number of suburbs have a North/South split, include if needed.

## Sensors Created

This version will create 4 sensors & 6 binary sensors

* sensor.act_garbage_last_updated
* sensor.act_garbage_pickup
* sensor.act_recycling_pickup
* sensor.act_greenwaste_pickup
* binary_sensor.act_garbage_today
* binary_sensor.act_garbage_tomorrow
* binary_sensor.act_recycling_today
* binary_sensor.act_recycling_tomorrow
* binary_sensor.act_greenwaste_today
* binary_sensor.act_greenwaste_tomorrow

## Issues/Feature Requests

Please log any issues or feature requests in this GitHub repository for me to review.