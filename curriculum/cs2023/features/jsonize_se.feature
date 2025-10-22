Feature: JSONize SE knowledge area
  As a developer
  I want the SE knowledge area text files to be converted to v2 JSON
  So that the generated output validates against the v2 schema and can be used as golden files for tests

  Background:
    Given the v2 schema exists at "curriculum/cs2023/ka.schema.v2.json"
    And the parser script is available at "curriculum/cs2023/direct_parse_v2.py"

  Scenario: Convert a single KA text file to v2 JSON
    Given I have a single KA text file "input/SE_sample.txt" containing a title, a summary paragraph, and bullet learning outcomes
    When I run the parser script
    Then the file "curriculum/SE.golden.v2.json" should be created
    And the output should be non-empty
    And the output should validate against the v2 schema

  Scenario: Convert multiple KA text files
    Given I have multiple text files in "input/" (e.g. SE.txt, SE_extra.txt)
    When I run the parser script
    Then the output JSON should contain one object per input file
    And each object should contain the keys required by the v2 schema (id, title, summary, learning_outcomes)

  Scenario: Handle malformed input gracefully
    Given an input file contains no bullets or paragraphs
    When I run the parser script
    Then the parser should include the file in output with empty or null fields for the missing items
    And the test should flag this as an edge case but not crash the parser

  Scenario: CI-friendly validation run
    Given a CI environment runs the parser in "dry-run" or limited mode
    When the parser runs
    Then it should produce a small output and validate against the schema
    And the CI job should fail if validation fails
