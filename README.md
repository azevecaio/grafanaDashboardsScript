#NGSX Grafana Dashboards
----------------------------------

##Using Executable (.exe)
###Run
* Execute: grafana.exe 

###Advanced Execution
Example:
- grafana.exe -b --orgs 0
- grafana.exe -u --orgs 21 --dashboards 0
- grafana.exe -c --orgs 22 --tags 5,15

----------------------------------
##Using Python
###Instalation
* Install Miniconda
* conda create --name <env> --file requirements.txt
* conda activate <env>

###Run
* Execute main file: python grafana_main.py

###Advanced Execution
Example:
- python grafana_main.py -b --orgs 0
- python grafana_main.py -u --orgs 21 --dashboards 0
- python grafana_main.py -c --orgs 22 --tags 5,15