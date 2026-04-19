*** Settings ***
Resource    variables.robot
Library    RequestsLibrary
Library    JSONLibrary
Library    apis.payment_api.PaymentAPI    base_url=${BASE_URL}
Library    steps.payment_validation.PaymentValidation
Library    Collections
Library    String

*** Keywords ***
Suite Setup For Payment API
    [Documentation]    Verify mock server is up, then create HTTP session.
    Ensure Server Available
    Create Session    ${SESSION}    ${BASE_URL}

We Request Payment For Scenario
    [Documentation]    GET /payment/ for given scenario; store response in \${payment_response}.
    [Arguments]    ${scenario}
    ${params}=    Create Dictionary    CellNumber=${CELL_NUMBER}    scenario=${scenario}
    ${resp}=    GET On Session    ${SESSION}    /payment/    params=${params}
    ${payment_response}=    Convert String To JSON    ${resp.text}
    Set Test Variable    ${payment_response}    ${payment_response}

We Request Payment For Scenario Expecting Status
    [Documentation]    GET /payment/ for given scenario and assert HTTP status.
    [Arguments]    ${scenario}    ${expected_status}
    ${params}=    Create Dictionary    CellNumber=${CELL_NUMBER}    scenario=${scenario}
    ${err}=    Run Keyword And Expect Error    *    GET On Session    ${SESSION}    /payment/    params=${params}
    Should Contain    ${err}    ${expected_status}

We Validate All Payment Rules
    [Documentation]    Run R1–R7 validation on \${payment_response}.
    Validate All Rules    ${payment_response}

Validation Should Pass
    [Documentation]    Assert no validation errors (positive case).
    Log    Validation passed (no assertion errors).

We Run Validation And Capture Error
    [Documentation]    Run validation expecting failure; store error in \${validation_error}.
    ${err}=    Run Keyword And Expect Error    *    Validate All Rules    ${payment_response}
    Set Test Variable    ${validation_error}    ${err}

The Error Message Should Contain
    [Documentation]    Assert validation error message contains expected text.
    [Arguments]    ${expected}
    Should Contain    ${validation_error}    ${expected}
