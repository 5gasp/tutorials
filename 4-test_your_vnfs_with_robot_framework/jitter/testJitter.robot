*** Settings ***
Library        jitter.py

*** Test Cases ***
Testing if the jitter is %{jitter_comparator} %{jitter_threshold} ms
    ${COMPARATOR}=       Run Keyword If      '%{jitter_comparator}' == 'more_than'        Set Variable    >
    ...    ELSE IF    '%{jitter_comparator}' == 'more_or_equal_than'        Set Variable    >=
    ...    ELSE IF    '%{jitter_comparator}' == 'less_than'        Set Variable    <
    ...    ELSE IF    '%{jitter_comparator}' == 'less_or_equal_than'        Set Variable    <=
    ...    ELSE     Fail  \nComparator has not been defined


    ${jitter_ms}=    jitter
    IF     '${jitter_ms}' != '-1'
    Should Be True    ${jitter_ms} ${COMPARATOR} %{jitter_threshold}
    ELSE
    FAIL    \nImpossible to compute Jitter
    END