from awxkit import api
from awxkit import pages

 # Initialize the connection to Ansible Tower
 tower = awxkit.api.Api(
     base_url='https://your-ansible-tower-url',
     username='your-username',
     password='your-password',
     verify_ssl=False  # Set to True if using a valid SSL certificate
 )

 # Define the project parameters
 project_data = {
     'name': 'My Basic Project',
     'description': 'A basic project created via API',
     'organization': 1,  # Replace with your organization ID
     'scm_type': 'git',
     'scm_url': 'https://github.com/your-repo.git',
     'scm_branch': 'main',
     'scm_update_on_launch': True
 }

 # Create the project
 project = tower.projects.post(project_data)

 # Output the result
 print(f"Project created: {project.json['name']} with ID {project.json['id']}")
