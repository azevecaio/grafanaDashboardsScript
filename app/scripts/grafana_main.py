from cmath import exp
import requests, sys
import argparse

session = requests.Session()

parser = argparse.ArgumentParser()

action = parser.add_mutually_exclusive_group()
mode = parser.add_mutually_exclusive_group()
newOrg = parser.add_mutually_exclusive_group()

def init(*args):
    '''Handle args and creating menus'''
    action.add_argument("-c", "--create", action='store_true', help="Create dashboards")
    action.add_argument("-u", "--update", action='store_true',  help="Update dashboards")
    action.add_argument("-b", "--backup", action='store_true', help="Backup dashboards")
    parser.add_argument("--orgs", type=str, help="Organizations index separeted by commas (Note: Index can be change). Use 0 for all")
    mode.add_argument("--tags", type=str, help="Tags index separeted by commas (Note: Index can be change). Use 0 for all", required=False)
    mode.add_argument("--dashboards", type=str, help="Dashboards index separeted by commas (Note: Index can be change). Use 0 for all", required=False)
    
    newOrg.add_argument("-no", "--neworg", action='store_true', help="Create new organization", required=False)

    args = parser.parse_args()

    import grafana_organization as organization

    template = organization.Organization(session, "Template")
    template.createToken()
    template.getDashboards()

    import grafana_middleware as middleware


    #Handling arguments
    try:
        if args.neworg:
            organization.Organization.createOrganization(session, input('Nome da organização: '))

        if args.create or args.update or args.backup:
            middleware.executedByCmd(session, args, template)
        else:
            middleware.executedByWizard(session, template)

        template.deleteToken()

    except Exception as e:
        print(e)
        template.deleteToken()
        sys.exit()

    except KeyboardInterrupt:
        print("Ctrl + C")
        template.deleteToken()
        sys.exit()

if __name__ == "__main__":
    try:
        init()
    except Exception as e:
        print(e)
        sys.exit()