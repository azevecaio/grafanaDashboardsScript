from ast import Or
import credentials as cred
import json, os

class Organization:
    domain, user, password = cred.validate_cred()
    
    host = f'https://{domain}/api'
    basicAuthUrl = f'https://{user}:{password}@{domain}'


    def __init__(self, session, organizationName):
        self.host = f'https://{self.domain}/api'
        self.org = organizationName
        self.session = session
        self.basicAuthUrl = f'https://{self.user}:{self.password}@{self.domain}'
        self.jsonData = self.getOrganizationByName()
        self.headersOrgId = {'X-Grafana-Org-Id': str(self.jsonData['id'])}

    @classmethod
    def createOrganization(cls, session, organizationName):
        json = {'name': f"{organizationName}"}
        response = session.post(url=cls.basicAuthUrl+'/api/orgs', json=json, verify=False)

    def getOrganizationByName(self):
        '''Get all orgs from the user'''
        response = self.session.get(url=self.basicAuthUrl+'/api/orgs/name/'+self.org, verify=False)
        return response.json()

    def getOrganizations(self, *exclusions):
        '''Get all orgs excluding the exceptions'''
        orgs = []
        response = self.session.get(url=self.basicAuthUrl+'/api/orgs', verify=False)
        for org in response.json():
            if org['name'] in exclusions:
                continue
            orgs.append(org)
        return orgs

    def getToken(self, *filter):
        '''Get API Token in a organization'''
        response = self.session.get(url=self.basicAuthUrl+'/api/auth/keys', headers=self.headersOrgId, verify=False)
        for apiKey in response.json():
            if filter[0] in apiKey['name']:
                return apiKey

    def createToken(self):
        '''Create API Token in a organization'''
        json = {'name': 'Python-' + self.jsonData['name'] + '-Key','role': "Admin"}
        try:
            response = self.session.post(url=self.basicAuthUrl+'/api/auth/keys', headers=self.headersOrgId, json=json, verify=False)
            self.jsonData['apiKey'] = response.json()
            return {"message": f"API Token criado na organização - {self.jsonData['name']}"}
        except Exception as e:
            print(e)
            return {"message": f"Erro ao criar API Token na organização - {self.jsonData['name']}"}

    def deleteToken(self):
        '''Delete API Token in a organization'''
        try:
            response = self.session.delete(
                url=self.basicAuthUrl+'/api/auth/keys/'+ str(self.jsonData['apiKey']['id']),
                headers=self.headersOrgId,
                verify=False
                )
            self.jsonData.pop('apiKey')
            reponseJson = response.json()
            return {"message": f"Token removido da organização - {self.jsonData['name']}"}
        except Exception as e:
            print(e)
            return {"message": f"Erro ao remover a chave API da organização {self.jsonData['id']}"}

    def getDashboards(self, *exclusions):
        '''Get all dashboards from the Org'''
        headersAuthorization = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.jsonData['apiKey']['key'])
            }
        response = self.session.get(url=self.host+'/search', headers=headersAuthorization, verify=False)        
        listDashboards = []
        for dash in response.json():
            try:
                if dash['type'] == 'dash-db':
                    if dash['title'] in exclusions:
                        continue
                    listDashboards.append(dash)
            except KeyError:
                pass
        self.jsonData['dashboards'] = listDashboards
        return listDashboards

    def getDashboardContents(self, dashboard):
        '''Get all dashboards content from the dashboard'''
        headersAuthorization = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.jsonData['apiKey']['key'])
            }
        response = self.session.get(url=self.host+'/dashboards/uid/'+dashboard['uid'], headers=headersAuthorization, verify=False)
        contentJson = response.json()['dashboard']
        try:
            currents = contentJson['templating']['list']
            #clearing values from current. When a dashboard is exported  all current variables are exported too and need to be cleared.
            for current in currents:
                current['current'] = {}
        except KeyError:
            pass
        return contentJson

    def createDashboards(self, folderId, contentJson):
        '''Create the dashboard in a organization'''
        headersAuthorization = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.jsonData['apiKey']['key'])
            }
        contentJson['id'] = None
        title = contentJson['title']
        content = {
            "dashboard": contentJson,   
            "folderId": folderId,
            "overwrite": True
            }

        response = self.session.post(url=self.host+'/dashboards/db', json=content, headers=headersAuthorization, verify=False)
        print(f'The dashboard {title} was created/updated successfully!')

    def deleteDashboard(self, dashboard):
        headersAuthorization = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.jsonData['apiKey']['key'])
            }
        uid = dashboard['uid']
        response = self.session.delete(url=f'{self.host}/dashboards/uid/{uid}', headers=headersAuthorization, verify=False)
        return response

    def dashboardsBackup(self, directory):
        '''Creates a dashboard backup file from the organization that was provided the API Key'''

        for dashboard in self.jsonData['dashboards']:
            contentJson = self.getDashboardContents(dashboard)
            self.saveToFile(contentJson, directory)       
        
    def saveToFile(self, contentJson, directory):
        '''
        Create a file with the dashboard content.
        '''
        if not os.path.exists(directory):
            os.makedirs(directory)
        content = json.dumps(contentJson, indent=4)
        title = contentJson['title']+'.json'
        with open(directory+os.sep+title,'w') as file:
            file.write(content)
            file.close() 
        print(f'The file {title} was created successfully!')

    def getFolders(self):
        '''Get all folders from the Org'''
        headersAuthorization = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.jsonData['apiKey']['key'])
            }
        response = self.session.get(url=self.host+'/folders', headers=headersAuthorization, verify=False)
        self.jsonData['folders'] = response.json()

    def createFolders(self, folder):
        '''Create a folder in a organization'''
        headersAuthorization = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.jsonData['apiKey']['key'])
            }
        title = folder['title']
        try:
            response = self.session.post(url=self.host+'/folders', headers=headersAuthorization, json=folder, verify=False)
            print(f'The folder {title} was created successfully!')
        except Exception as e:
            print(e)
        return response.json()
    
    def importDashboards(self, template, dashboards, action=''):
        '''Get dashboards from the Template Organization and import in the new one based on API KEY. If action parameter set True will not create the dashboard.'''
        
        self.getDashboards()
        self.getFolders()

        template.getFolders()

        for dashboard in dashboards:
            dashboardTitle = dashboard['title']
            dashboardTags = dashboard['tags']

            #Find folders on template and create on new organization based on chosen dashboards
            for folder in template.jsonData['folders']:
                if folder['title'] in [newOrgFolder['title'] for newOrgFolder in self.jsonData['folders']]:
                    continue
                #Little Teste or litteteste in tags
                if action == 'Update':
                    continue
                #Little Teste or litteteste in tags
                if folder['title'] in dashboardTags or folder['title'].replace(" ", "").lower() in dashboardTags:
                    self.createFolders(folder)

            #Recreate dashboard with different UID
            for newOrgDashboard in self.jsonData['dashboards']:
                newOrgDashboardTitle = newOrgDashboard['title']
                if dashboardTitle ==  newOrgDashboardTitle and dashboard['uid'] != newOrgDashboard['uid']:
                    self.deleteDashboard(newOrgDashboard)
                    print(f'The dashboard {dashboardTitle} was already exists but the uid is different, will be recreated.')

            if dashboardTitle not in getListKey(self.jsonData['dashboards'], 'title') and action=='Update':
                print(f"{dashboardTitle} dashboard does not exist in organization")
                continue

            #Get dashboard content
            contentJson = template.getDashboardContents(dashboard)
            self.getFolders()

            folderId = 0

            #Get the folder ID on new Organization to create dashboards on right folder
            for folder in self.jsonData['folders']:
                folderTitle = folder['title']
                if folderTitle in dashboardTags or folderTitle.replace(" ", "").lower() in dashboardTags :
                    folderId = folder['id']

            self.createDashboards(folderId, contentJson)
            
def getListKey(listDict, key):
    listKeys = []
    for item in listDict:
        listKeys.append(item[key])
    return listKeys

def compareFolders(uid, foldersNew):
    '''If folder already have an UID get the ID from the new org and set in the new dashboard.'''
    for i in range(len(foldersNew)):
        if uid == foldersNew[i]['uid']:
            return foldersNew[i]['id']