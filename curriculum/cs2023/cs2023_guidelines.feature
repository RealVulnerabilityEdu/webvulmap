Feature: Download CS2023 Curriculum Guidelines PDF

  As a computer science educator
  I want to download the official CS2023 Curriculum Guidelines PDF
  So that I can access the latest curriculum recommendations for my courses

  Scenario: Download the CS2023 PDF file  
    Given I have the official URL for the CS2023 Curriculum Guidelines PDF
    When I run the downloader script
    Then the PDF file should be saved to the curriculum/cs2023 directory
    And the script should handle errors gracefully

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