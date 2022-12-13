
import sys, os
import grafana_organization as organization

def separationLine(size=42):
    print("-" * size)

def createMenuFromDict(items):
    #Creating menu with all organizations
    """
    0 - All
    1 - ORG1
    2 - ORG2
    3 - ORG3
    """
    separationLine()
    items.insert(0, {'id': 0, 'name': 'All'})
    for item in items:
        print(f'{item["id"]} - {item["name"]}')
    separationLine()

    userInput = input('Insert all values separate by commas: ')
    userPick = userInput.split(',')
    choice = []

    for pick in userPick:
        for item in items:
            if str(item["id"]) == str(pick):
                choice.append(item)
    return choice

def welcomeMenu():
    #Welcome menu
    separationLine()
    print("Welcome to python Grafana")
    separationLine()

    actionsList = {
        0: "Exit",
        1: "Create",
        2: "Update",
        3: "Backup"
        }

    for index, action in actionsList.items():
        if index == 0:
            print(f'{index} - {action}')
        else:
            print(f'{index} - {action} dashboards')
    separationLine()

    actionChosen = int(input('Option: '))
    if actionChosen > int(index) or actionChosen < 0:
        raise ValueError('Insert a valid option')
        
    return actionsList[actionChosen]

def secondMenu():
    #Actions by Tag or dashboard 
    createByList = {
        0: "Exit",
        1: "Tags", 
        2: "Dashboards"
    }

    for index, createBy in createByList.items():
        if index == 0:
            print(f'{index} - {createBy}')
        else:
            print(f'{index} - Import by {createBy} ')
    separationLine()

    userInput = int(input('Option: '))
    if userInput > index or userInput < 0:
        raise ValueError('Insert a valid option')

    return createByList[userInput]

def getItemListByTagOrDashboard(organization, actionBy):
    #Show Tag or Dashboards values Menu
    values = []
    items = organization.jsonData['dashboards']
    if actionBy == 'Tags':
            for item in items:
                values += item['tags']

    elif actionBy == 'Dashboards':
        for item in items:
            values.append(item['title'])
    
    else:
        organization.deleteToken()
        sys.exit("Invalid choice")

    valuesWithoutDuplicates = sorted(list(set(values)))
    itemList = []
    for index, value in enumerate(valuesWithoutDuplicates):
        tempDict = {}
        tempDict['id'] = index + 1
        tempDict['name'] = value
        itemList.append(tempDict)
    
    return itemList

def executedByWizard(session, template):
    #Show Welcome menu and get an answer
    action = welcomeMenu()
    if action == 'Exit':
        print("Saindo ...")
        template.deleteToken()
        sys.exit(1)

    #Show Second menu. Actions take by tag or daskboard and get an answer
    if action != 'Backup':
        actionBy = secondMenu()
        if actionBy == 'Exit':
            print("Saindo ...")
            template.deleteToken()
            sys.exit(1)

    orgList = template.getOrganizations('Template') if action != "Backup" else template.getOrganizations()
    
    #Show Organization menu
    organizationChosen = createMenuFromDict(orgList)

    if action != 'Backup':
        #Show Tag or Dashboards values menu
        itemList = getItemListByTagOrDashboard(template, actionBy)
        dashboardsChosen = createMenuFromDict(itemList)

    if action == 'Create' or action == 'Update':
        #Creating
        if {'id': 0, 'name': 'All'} in organizationChosen:
            choiceOrgs = [orgs for orgs in orgList if orgs.get('id') != 0]

        else:
            choiceOrgs = organizationChosen

        for org in choiceOrgs:
            #Using All option
            dashboardsToBeCreated = []
            if {'id': 0, 'name': 'All'} in dashboardsChosen:
                dashboardsToBeCreated = choiceOrgs = template.jsonData['dashboards']
            
            #By tags
            if actionBy == 'Tags':
                for choice in dashboardsChosen:
                    for dashboard in template.jsonData['dashboards']:
                        if choice['name'] in dashboard['tags']:
                            dashboardsToBeCreated.append(dashboard)


            #By dashboards
            if actionBy == 'Dashboards':
                for choice in dashboardsChosen:
                    for dashboard in template.jsonData['dashboards']:
                        if choice['name'] == dashboard['title']:
                            dashboardsToBeCreated.append(dashboard)
            

            print('----------- Organization ' + org['name'] + ' -----------')

            _org = organization.Organization(session, org['name'])
            _org.createToken()
            
            try:
                _org.importDashboards(template, dashboardsToBeCreated, action=action)
                _org.deleteToken()
            except Exception as e:
                print("Verifique as permissões do usuário a organização!")
                print(e)
                _org.deleteToken()

    if action == 'Backup':

        if {'id': 0, 'name': 'All'} in organizationChosen:
            choiceOrgs = orgList

        else:
            choiceOrgs = organizationChosen

        for org in choiceOrgs:
            print('----------- Organization ' + org['name'] + ' -----------')

            _org = organization.Organization(session, org['name'])
            _org.createToken()
            
            try:
                _org.getDashboards('Início')
                directory = os.path.abspath(org['name']+'-JsonFiles')
                _org.dashboardsBackup(directory)
                _org.deleteToken()
            except Exception as e:
                print("Verifique as permissões do usuário a organização!")
                print(e)
                _org.deleteToken()

def executedByCmd(session, args, template):
    '''Running by command line'''
    if args.create or args.update:
        #Ensure that parameter exist
        assert args.dashboards or args.tags and args.orgs

        #Get dashboards from dict
        dashboardsChosen = args.dashboards.split(',') if args.dashboards else args.tags.split(',')
        itemList = getItemListByTagOrDashboard(template, 'Tags' if args.tags else 'Dashboards')
        dashboards = []
        for choice in dashboardsChosen:
            for dash in itemList:
                if dash['id'] == int(choice):
                    dashboards.append(dash)


        #Get organization from dict
        orgList = template.getOrganizations('Template')
        organizationChosen = args.orgs.split(',')
        organizations = []
        for choice in organizationChosen:
            for org in orgList:
                if org['id'] == int(choice):
                    organizations.append(org)


        if '0' in organizationChosen:
            choiceOrgs = orgList

        else:
            choiceOrgs = organizations

        for org in choiceOrgs:

            #Using All option
            dashboardsToBeCreated = []
            if '0' in dashboardsChosen:
                dashboardsToBeCreated = template.jsonData['dashboards']

            #By tags
            if args.tags:
                for choice in dashboards:
                    for dashboard in template.jsonData['dashboards']:
                        if choice['name'] in dashboard['tags']:
                            dashboardsToBeCreated.append(dashboard)


            #By dashboards
            if args.dashboards:
                for choice in dashboards:
                    for dashboard in template.jsonData['dashboards']:
                        if choice['name'] == dashboard['title']:
                            dashboardsToBeCreated.append(dashboard)


            print('----------- Organization ' + org['name'] + ' -----------')

            _org = organization.Organization(session, org['name'])
            _org.createToken()
            
            try:
                _org.importDashboards(template, dashboardsToBeCreated, action='Create' if args.create else 'Update')
                _org.deleteToken()
            except Exception as e:
                print("Verifique as permissões do usuário a organização!")
                print(e)
                _org.deleteToken()
        
    if args.backup:

        #Get organization from dict
        orgList = template.getOrganizations()
        organizationChosen = args.orgs.split(',')
        organizations = []
        for choice in organizationChosen:
            for org in orgList:
                if org['id'] == int(choice):
                    organizations.append(org)
        
        if '0' in organizationChosen:
            choiceOrgs = orgList

        else:
            choiceOrgs = organizations

        for org in choiceOrgs:
            print('----------- Organization ' + org['name'] + ' -----------')

            _org = organization.Organization(session, org['name'])
            _org.createToken()
            
            try:
                _org.getDashboards('Início')
                directory = os.path.abspath(org['name']+'-JsonFiles')
                _org.dashboardsBackup(directory)
                _org.deleteToken()
            except Exception as e:
                print("Verifique as permissões do usuário a organização!")
                print(e)
                _org.deleteToken()

def getListKey(listDict, key):
    '''Get a List of Dict and return another list only with Keys'''
    listKeys = []
    for item in listDict:
        listKeys.append(item[key])
    return listKeys