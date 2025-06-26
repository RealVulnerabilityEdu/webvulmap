Feature: Download CS2023 Curriculum Guidelines PDF

  As a computer science educator
  I want to download the official CS2023 Curriculum Guidelines PDF
  So that I can access the latest curriculum recommendations for my courses

  Scenario: Download the CS2023 PDF file
    Given I have the official URL for the CS2023 Curriculum Guidelines PDF
    When I run the downloader script
    Then the PDF file should be saved to the curriculum/cs2023 directory
    And the script should handle errors gracefully