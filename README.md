# ReconMaster
ReconMaster is an automated reconnaissance web application that performs active reconnaissance on the provided domain and displays the results in user friendly manner.

Here is a brief description about the project aloong with relevant screenshots.

Register Page
- Users should first of all create an account in the system before logging in.

![register_account](https://user-images.githubusercontent.com/54204886/225201098-60800447-4bba-4cef-939b-2062d6deb02b.jpg)


Login Page
- Once account is created, user can login with the same set of credentials and will be redirected to their own dashboard.

![loginpage](https://user-images.githubusercontent.com/54204886/225201048-2f04e6b1-0ec3-4ee9-ad49-c8c036985fa3.jpg)


Reset password
- The application also allows us to reset password of the user via sending password reset link to the specified email addresses.

![password_reset](https://user-images.githubusercontent.com/54204886/225201374-7b881a94-dc5f-49dc-9a25-f239bc4c8860.jpg)


Dashboard
- Dashhboard is divided into two different parts. 
- The four boxes at the top displays summary of overall scan. It includes Total Targets Scanned, Total Subdomains Discovered, Total Endpoints Discovered, Total Currently Running Scans.
- The table below this displays all the recently scanned target with their additional information such as Domain name, Description, Last Scanned Time, and Scan Status.

![Dashboard](https://user-images.githubusercontent.com/54204886/225201134-779177b2-6069-4d0d-9708-0dcf8458fb7a.png)


Add Target
- Before Launching any scan, users should add target. The system takes domain name as a target. In addition, users can also add short description about the domain, but this is totally optional.

![Add_target](https://user-images.githubusercontent.com/54204886/225201225-4c9e8ee5-c075-4edf-b4a5-7dd5c9de1e24.png)


List Targets
- Once we have added the target, we need to check if the target was added successfully or not by navigating to list targets page. This page displays all the previously added targets along with additional information such as Added Date, Last Scanned date, and action column. From action column, we can either delete the target or Launch scan.

![list_targets](https://user-images.githubusercontent.com/54204886/225201259-f5cb6672-cfd9-4e09-8f9c-ed297950cdfc.png)


Scan History
- It is necessay to keep track of previous scans. Thus, scan history page was created. It lists all the targets that was scanned in the past along with scans that are running currently. In addition, we can also remove the target from scan history list from the action section. Moreover, to view the detailed scan result, we should click on view button.

![scan_history](https://user-images.githubusercontent.com/54204886/225201299-a07eb8d6-e88a-4572-b473-bcd1764b0f90.png)


Scan Result
- This page displays results of the completed scan. At top, it gives summary of task completion along with total number of subdomain and endpoints discovered.
- Below, fields namely subdomain, IP Address, Status, Ports, Content Length, Page Title, Technology, and Screenshot are displayed. Apart from that, there is an option to export list of subdomains and URLs for future analysis.


![scan_results](https://user-images.githubusercontent.com/54204886/225204358-3bb33f5e-5f8c-40cb-9058-c508e3c85631.png)

## DEMO
A short demo explaning different components this web application can be found [here](https://1drv.ms/v/s!AolcY885WF6Twy7_gIrdI_xuJgl_?e=TnVKs8) in Nepali.
 
