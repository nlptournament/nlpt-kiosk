# Error-Codes returend by Element-validation

## Generic

  * **1**: *(any)* marked as not to be None
  * **2**: *(any)* marked as unique, but element with value "<value\>" allready present
  * **3**: *(any)* needs to be of type <type\>[ or None]
  * **4**: *(any)* There is no <element-name\> with id '<element-id\>'
  * **5**: *(any)* needs to be one of: <list-of-valid-values\>
  * **6**: *(any)* not allowed to be empty
  * **7**: *(any)* generic range error like: needs do be bigger/smaller/in range...

## Session(Base)

*reserved range **1x** for individual errors*

  * **4**: *(user_id)* There is no User with id '<element-id\>'
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