# Error-Codes returend by Element-validation

## Generic

  * **1**: *[ElementBase]* marked as not to be None
  * **2**: *[ElementBase]* marked as unique, but element with value "<value\>" allready present
  * **3**: *[ElementBase]* needs to be of type <type\>[ or None]
  * **4**: *[ElementBase]* there is no <element-name\> with id '<element-id\>'
  * **5**: *[any]* needs to be one of: <list-of-valid-values\>
  * **6**: *[any]* not allowed to be empty
  * **7**: *[any]* generic range error like: needs do be bigger/smaller/in range...

## Session(Base)

*reserved range **1x** for individual errors*

  * **4**: *(user_id)* there is no User with id '<element-id\>'
  * **10**: *(till)* needs to be in the future
  * **11**: *(ip)* does not match with the IP of request

## Setting(Base)

*reserved range **2x** for individual errors*

  * **3**: *(value)* needs to be of type <choosen-type\> or None
  * **5**: *(type)* needs to be one of: [str, int, float, bool]

## User

*reserved range **3x** for individual errors*

## ScreenTemplate

*reserved range **4x** for individual errors*

  * **3**: *(variables_def)* parameter 'type' in definition of '<name-of-variable\>' needs to be of type str
  * **5**: *(variables_def)* parameter 'type' in definition of '<name-of-variable\>' needs to be one of: <list-of-allowed-types\>
  * **6**: *(key)* not allowed to be empty
  * **7**: *(duration)* needs to be bigger than 0 or Null
  * **40**: *(variables_def)* missing the parameter 'type' in definition of '<name-of-variable\>'
  * **41**: *(variables_def)* default value in definition of '<name-of-variable\>' is not of type '<defined-type\>'
  * **42**: *(variables_def)* '<name-of-variable\>' is defined to be readonly, but default value is missing

## Screen

*reserved range **5x** for individual errors*

  * **7**: *(duration)* needs to be bigger than 0 or Null
  * **7**: *(repeat)* needs to be 0 or bigger
  * **3**: *(variables)* '<name-of-variable\>' needs to be of type <type\>
  * **50**: *(_id)* Screen can't be changed, as it is used in a locked Timeline
  * **51**: *(variables)* missing the variables: <list-of-variables-names\>

## TimelineTemplate

*reserved range **6x** for individual errors*

## Timeline

*reserved range **7x** for individual errors*

  * **7**: *(start_pos)* needs to be 0 or bigger
  * **7**: *(current_pos)* needs to be 0 or bigger
  * **70**: *(_id)* Timeline can't be changed, as it is locked

## Kiosk

*reserved range **8x** for individual errors*

  * **80**: *(timeline_id)* Timeline is part of a Preset and therefore can't be displayed

### element delete error-codes

  * **1**: at least one locked Screen is using this <element-name\>
  * **2**: can't be deleted as it is locked

## Media

*reserved range **8x** for individual errors*

  * **5**: *(src_type)* needs to be one of: [0, 1]
  * **5**: *(type)* needs to be one of: [0, 1, 2]
