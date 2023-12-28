This is a script to automate production of the implementation tracker as part of the 'automate' your Datadog apm installation effort.

1. This script is fed by the data.json file, which is created from the xlsx_to_json.py file.
2. the xlsx file that should be parsed to json is dumped either from the form / or from a provided list. Right now this script is made to parse from a provided xlsx script, however adding the additional lines to the form is a small and simple refactor.
3. Use the Makefile to create to xlsx doc. ('make' will build your tracker. 'make all' will remove any existing tracker that occupies the tracker namespace build and clean will just remove a tracker that occupies the required namespace)

PURPOSE:
As the implementation effort increases and/or the action of performing the implementation is moved directly to forest service, the tracker with required steps can be created with little effort.

TODO:
1. data validation for the form (which should be the next step in feeding this tracker). Currently for the 'Location field' (which is commented out), the 'ServerCount' field serves as a partial field for 'which cloud provider' (location) the service / application that is being instrumented lives in.
2. Form State. There have been 2 manual completions of the form (by way of printing the pdf and then emailing a photo copy) due to the length of the form. This should be addressed to see if there is a way to save state in the form, or begin a policy of not accepting printed pdfs.
3. Tie this into an ansible playbook that can execute the agent installation and or apm configuration modification.
