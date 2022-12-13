# NGSX Grafana Dashboards
----------------------------------

## Using Executable (.exe)
Run: grafana.exe 

Advanced Execution
Example:

<code> grafana.exe -b --orgs 0 </code>

<code> grafana.exe -u --orgs 21 --dashboards 0 </code>

<code> grafana.exe -c --orgs 22 --tags 5,15 </code>

----------------------------------
## Using Python
### Instalation
* Install Miniconda
- $ conda create --name env --file requirements.txt
- $ conda activate env
- $ pip install argparse

Run: Execute main file: python grafana_main.py

Advanced Execution
Example:

<code> python grafana_main.py -b --orgs 0 </code>

<code> python grafana_main.py -u --orgs 21 --dashboards 0 </code>

<code> python grafana_main.py -c --orgs 22 --tags 5,15 </code>
