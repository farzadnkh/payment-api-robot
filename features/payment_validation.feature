Feature: Checkout Payment API validation
  Validate payment endpoint response schema, types, and business rules (R1–R7).
  Technical actions (HTTP via RequestsLibrary, JSON parsing, validations) are in steps/ and apis/.

  Scenario: S1 Happy path – online, wallet, BNPL present and all clickable
    Given we request payment for scenario "s1"
    When we validate all payment rules
    Then validation should pass

  Scenario: S2 BNPL blocked – method not selectable, options may be empty
    Given we request payment for scenario "s2"
    When we validate all payment rules
    Then validation should pass

  Scenario: S3 Insufficient credit – option with credit=0 is ineligible by R5
    Given we request payment for scenario "s3"
    When we validate all payment rules
    Then validation should pass

  Scenario: S4 Non-active option – option with is_active=false is ineligible by R5
    Given we request payment for scenario "s4"
    When we validate all payment rules
    Then validation should pass

  Scenario: S5 Default option invalid – multiple is_default=true among eligible (R6)
    Given we request payment for scenario "s5"
    When we run validation and capture error
    Then the error message should contain "R6"

  Scenario: S6 Missing required field – payment_methods[0] missing type/title
    Given we request payment for scenario "s6"
    When we run validation and capture error
    Then the error message should contain "missing required field"

  Scenario: S7 Wrong type – id string, is_clickable string
    Given we request payment for scenario "s7"
    When we run validation and capture error
    Then the error message should contain "must be"

  Scenario: S8 Non-success HTTP – body.status != 200
    Given we request payment for scenario "s8"
    When we run validation and capture error
    Then the error message should contain "status"
