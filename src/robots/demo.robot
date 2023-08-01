*** Settings ***
Documentation       This is a demo
Library             Process


*** Variables ***
${URL}      http://localhost:8090/tasks/


*** Test Cases ***
Just a demo:
    ${result}=  Run Process     curl    ${URL}
    Log         all ouput: ${result.stdout}
    Should Be Equal As Strings      "${result.stdout}"    "help ...."
