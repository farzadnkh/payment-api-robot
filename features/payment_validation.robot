*** Settings ***
Resource    ../resources/payment_resources.robot
Suite Setup    Suite Setup For Payment API

*** Test Cases ***
S1 Happy path – online, wallet, BNPL present and all clickable
    [Tags]    S1    positive
    [Documentation]    Rules OK
    We Request Payment For Scenario    s1
    We Validate All Payment Rules
    Validation Should Pass

S2 BNPL blocked – method not selectable, options may be empty
    [Tags]    S2    positive
    [Documentation]    Method treated as not selectable; options may be empty
    We Request Payment For Scenario    s2
    We Validate All Payment Rules
    Validation Should Pass

S3 Insufficient credit – option with credit=0 ineligible by R5
    [Tags]    S3    positive    R5
    [Documentation]    Option marked ineligible by rule R5
    We Request Payment For Scenario    s3
    We Validate All Payment Rules
    Validation Should Pass

S4 Non-active option – option with is_active=false ineligible by R5
    [Tags]    S4    positive    R5
    [Documentation]    Option ineligible by rule R5
    We Request Payment For Scenario    s4
    We Validate All Payment Rules
    Validation Should Pass

S5 Default option invalid – multiple is_default=true among eligible (R6)
    [Tags]    S5    negative    R6
    [Documentation]    Fail with clear message (R6)
    We Request Payment For Scenario    s5
    We Run Validation And Capture Error
    The Error Message Should Contain    R6

S6 Missing required field – payment_methods[0] missing type/title
    [Tags]    S6    negative
    [Documentation]    Fail validation
    We Request Payment For Scenario    s6
    We Run Validation And Capture Error
    The Error Message Should Contain    missing required field

S7 Wrong type – id string, is_clickable string
    [Tags]    S7    negative
    [Documentation]    Fail type validation
    We Request Payment For Scenario    s7
    We Run Validation And Capture Error
    The Error Message Should Contain    must be

S8 Non-success – body.status != 200
    [Tags]    S8    negative
    [Documentation]    Fail fast with clear diagnostics
    We Request Payment For Scenario    s8
    We Run Validation And Capture Error
    The Error Message Should Contain    status

S9 HTTP 500 – transport failure
    [Tags]    S9    negative    http
    [Documentation]    HTTP 500 status from server
    We Request Payment For Scenario Expecting Status    s9    500

S10 Wallet rule violation – is_wallet true while type is not wallet
    [Tags]    S10    negative    R3
    [Documentation]    R3 violation when is_wallet=true and type!=wallet
    We Request Payment For Scenario    s_r3
    We Run Validation And Capture Error
    The Error Message Should Contain    R3
