Feature: Extract Knowledge Area sections from the CS2023 curriculum

  Scenario: Extract KAs from valid input and PDF
    Given the input file "knowledge_areas.json" contains valid entries
    And the CS2023 PDF file is present in the correct location
    When I run the KA extraction script
    Then text files like "SE_Software_Engineering.txt" and "SP_Security_and_Privacy.txt" should be created
    And each file should contain text from the corresponding page range

  Scenario: Handle missing input file
    Given the input JSON file is missing
    When I run the KA extraction script
    Then the script should report a "File not found" error and exit gracefully

  Scenario: Skip KA with invalid page range
    Given a KA has a begin-page greater than or equal to the end-page
    When I run the KA extraction script
    Then the script should skip that KA and print a warning

  Scenario: Sanitize special characters in filenames
    Given a KA has characters like :, &, (), or – in its name
    When I run the KA extraction script
    Then the output filename should be safely sanitized and created